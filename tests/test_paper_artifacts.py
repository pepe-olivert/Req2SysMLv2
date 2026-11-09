import math

import numpy as np
import pytest

from evaluation.make_paper_artifacts import (
    cochran_q,
    holm,
    is_degenerate,
    literal_share,
    mcnemar_exact,
)


def test_holm_adjusts_in_rank_order_and_keeps_monotonicity():
    # Sorted p: 0.01 (x3), 0.02 (x2) -> 0.04, 0.03 (x1) -> max(0.04, 0.03) = 0.04.
    assert holm([0.03, 0.01, 0.02]) == pytest.approx([0.04, 0.03, 0.04])


def test_holm_ignores_nan_and_caps_at_one():
    adjusted = holm([0.6, float("nan"), 0.4])
    assert adjusted[0] == pytest.approx(0.8) and adjusted[2] == pytest.approx(0.8)
    assert math.isnan(adjusted[1])
    assert holm([0.6, 0.7]) == pytest.approx([1.0, 1.0])


def test_cochran_q_matches_hand_computation():
    # Column sums 4, 4, 1 (T = 9); row sums squared add to 17: Q = 2 * (3 * 33 - 81) / (3 * 9 - 17) = 3.6.
    x = np.array([[1, 1, 0], [1, 0, 0], [1, 1, 1], [0, 1, 0], [1, 0, 0], [0, 1, 0]])
    q, dof, p = cochran_q(x)
    assert q == pytest.approx(3.6) and dof == 2
    assert 0 < p < 1


def test_cochran_q_is_undefined_when_all_blocks_agree():
    q, _, p = cochran_q(np.ones((4, 3)))
    assert math.isnan(q) and math.isnan(p)


def test_mcnemar_uses_only_discordant_pairs():
    a = [True] * 10 + [True] * 8 + [False] * 2
    b = [True] * 10 + [False] * 8 + [True] * 2
    assert mcnemar_exact(a, b) == pytest.approx(0.109375)  # binomial(8 of 10, p=0.5), two-sided
    assert mcnemar_exact([True, False], [True, False]) == 1.0


def test_degenerate_repair_keeps_less_than_half_of_the_code():
    assert list(is_degenerate([2000, 2000, 2000], [76, 1000, 1999])) == [True, False, False]


def test_literal_share_normalises_case_and_whitespace():
    reqs = ["The system SHALL   log every call.", "The driver shall acknowledge alarms."]
    code = 'requirement r1 { doc /* the system shall log every call. */ }'
    assert literal_share(reqs, code) == pytest.approx(0.5)
    assert math.isnan(literal_share([], code))
