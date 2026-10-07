from statistics import NormalDist


ALPHA = 0.05
TARGET_POWER = 0.80
_NORMAL = NormalDist()


def _clamp_probability(value: float) -> float:
    return min(max(float(value), 0.0), 1.0)


def _two_sided_z(alpha: float = ALPHA) -> float:
    return _NORMAL.inv_cdf(1.0 - alpha / 2.0)


def _power_for_effect(
    baseline_rate: float,
    absolute_effect: float,
    control_n: int,
    treatment_n: int,
    alpha: float = ALPHA,
) -> float:
    """Approximate two-sided normal-test power for a conversion-rate effect."""
    if control_n <= 0 or treatment_n <= 0:
        return 0.0

    baseline = _clamp_probability(baseline_rate)
    treatment = _clamp_probability(baseline + absolute_effect)
    z_critical = _two_sided_z(alpha)

    se_alt = (
        baseline * (1.0 - baseline) / control_n
        + treatment * (1.0 - treatment) / treatment_n
    ) ** 0.5

    if se_alt <= 0.0:
        return 1.0 if absolute_effect != 0 else 0.0

    noncentrality = abs(absolute_effect) / se_alt
    upper_tail = 1.0 - _NORMAL.cdf(z_critical - noncentrality)
    lower_tail = _NORMAL.cdf(-z_critical - noncentrality)
    return _clamp_probability(upper_tail + lower_tail)


def _positive_mde(
    baseline_rate: float,
    control_n: int,
    treatment_n: int,
    alpha: float = ALPHA,
    target_power: float = TARGET_POWER,
) -> float:
    """
    Approximate the smallest positive absolute conversion-rate uplift
    detectable at the requested power under a normal approximation.
    """
    if control_n <= 0 or treatment_n <= 0:
        return 1.0

    max_effect = max(1e-9, 1.0 - _clamp_probability(baseline_rate) - 1e-9)
    if _power_for_effect(
        baseline_rate,
        max_effect,
        control_n,
        treatment_n,
        alpha,
    ) < target_power:
        return max_effect

    low = 0.0
    high = max_effect

    # Binary search is fast and avoids a dependency on statsmodels.
    for _ in range(60):
        mid = (low + high) / 2.0
        power = _power_for_effect(
            baseline_rate,
            mid,
            control_n,
            treatment_n,
            alpha,
        )
        if power >= target_power:
            high = mid
        else:
            low = mid

    return high


def difference_in_proportions(
    control_n,
    control_success,
    treatment_n,
    treatment_success,
    *,
    alpha: float = ALPHA,
    target_power: float = TARGET_POWER,
):
    """
    Compare two independent conversion proportions.

    CI:
        Uses the standard unpooled normal approximation.

    Hypothesis test:
        Two-sided pooled two-proportion z-test:
        H0: p_treatment - p_control = 0
        H1: p_treatment - p_control != 0

    Power/MDE:
        Uses a normal approximation with the observed control rate as the
        planning baseline. The MDE is the smallest positive absolute uplift
        expected to reach the requested target power.
    """
    pc = control_success / control_n if control_n else 0.0
    pt = treatment_success / treatment_n if treatment_n else 0.0
    diff = pt - pc

    if control_n and treatment_n:
        se = (
            pc * (1.0 - pc) / control_n
            + pt * (1.0 - pt) / treatment_n
        ) ** 0.5
    else:
        se = 0.0

    if se <= 0.0:
        ci_low = diff
        ci_high = diff
    else:
        z_critical = _two_sided_z(alpha)
        ci_low = diff - z_critical * se
        ci_high = diff + z_critical * se

    # Pooled standard error is required for the null-based two-proportion test.
    pooled_denominator = control_n + treatment_n
    pooled = (
        (control_success + treatment_success) / pooled_denominator
        if pooled_denominator
        else 0.0
    )

    if control_n and treatment_n:
        pooled_se = (
            pooled * (1.0 - pooled)
            * (1.0 / control_n + 1.0 / treatment_n)
        ) ** 0.5
    else:
        pooled_se = 0.0

    if pooled_se <= 0.0:
        z_statistic = 0.0 if diff == 0.0 else float("inf")
        p_value = 1.0 if diff == 0.0 else 0.0
    else:
        z_statistic = diff / pooled_se
        p_value = 2.0 * (1.0 - _NORMAL.cdf(abs(z_statistic)))
        p_value = _clamp_probability(p_value)

    mde_absolute = _positive_mde(
        pc,
        control_n,
        treatment_n,
        alpha,
        target_power,
    )
    mde_relative = (
        mde_absolute / pc
        if pc > 0.0
        else None
    )

    return {
        "control_rate": pc,
        "treatment_rate": pt,
        "uplift": diff,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "hypothesis_test": {
            "test": "Two-proportion z-test",
            "null_hypothesis": "H0: treatment conversion = control conversion",
            "alternative_hypothesis": "H1: treatment conversion != control conversion",
            "alpha": alpha,
            "z_statistic": z_statistic,
            "p_value": p_value,
            "significant": bool(p_value < alpha),
        },
        "power_analysis": {
            "target_power": target_power,
            "baseline_rate": pc,
            "mde_absolute": mde_absolute,
            "mde_relative": mde_relative,
            "interpretation": (
                "Approximate minimum positive conversion-rate uplift detectable "
                f"with {target_power:.0%} power at alpha={alpha:.2f} under the "
                "normal approximation."
            ),
        },
    }


def segment_results(segments):
    result = []
    for segment, values in segments.items():
        control = [v for arm, v in values if arm == "control"]
        treatment = [v for arm, v in values if arm == "treatment"]
        if len(values) < 30 or not control or not treatment:
            continue
        cr = sum(control) / len(control)
        tr = sum(treatment) / len(treatment)
        result.append(
            {
                "segment": segment,
                "control_rate": cr,
                "treatment_rate": tr,
                "uplift": tr - cr,
                "n": len(values),
            }
        )
    return result
