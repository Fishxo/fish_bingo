"""
Build a predetermined call sequence so two cards can complete bingo on the same last number (admin test mode).
"""
from __future__ import annotations

from typing import List, Optional, Set, Tuple

from .game_logic import check_bingo_from_marked


def _enumerate_line_number_sets(layout, enabled_patterns: List[str]) -> List[Set[int]]:
    """Number sets for each winning line (matches check_bingo_from_marked)."""
    ep = set(enabled_patterns or ["horizontal", "vertical", "diagonal", "corner", "full_card"])
    lines: List[Set[int]] = []

    if not layout:
        return lines

    only_full = ep == {"full_card"}

    if not only_full and "horizontal" in ep:
        for row in layout:
            nums = {cell.get("number") for cell in row if cell.get("number") is not None}
            if nums:
                lines.append(nums)

    if not only_full and "vertical" in ep:
        for col_idx in range(5):
            nums = {
                layout[r][col_idx].get("number")
                for r in range(5)
                if layout[r][col_idx].get("number") is not None
            }
            if nums:
                lines.append(nums)

    if not only_full and "diagonal" in ep:
        d1 = {layout[i][i].get("number") for i in range(5) if layout[i][i].get("number") is not None}
        d2 = {layout[i][4 - i].get("number") for i in range(5) if layout[i][4 - i].get("number") is not None}
        if d1:
            lines.append(d1)
        if d2:
            lines.append(d2)

    if not only_full and "corner" in ep:
        corners = [layout[0][0], layout[0][4], layout[4][0], layout[4][4], layout[2][2]]
        nums = {cell.get("number") for cell in corners if cell.get("number") is not None}
        if nums:
            lines.append(nums)

    if "full_card" in ep:
        nums = {cell.get("number") for row in layout for cell in row if cell.get("number") is not None}
        if nums:
            lines.append(nums)

    # Dedupe identical lines
    seen = set()
    out: List[Set[int]] = []
    for s in lines:
        key = frozenset(s)
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def _try_order_before(
    U: Set[int],
    last_n: int,
    real_layout,
    fake_layout,
    game_id: int,
) -> Optional[List[int]]:
    """
    Find an order to call all numbers in U such that after each prefix, neither card has bingo.
    After full U, calling last_n completes both lines on the same number.
    """
    if not U:
        return []

    order: List[int] = []

    def backtrack(remaining: Set[int], called: Set[int]) -> bool:
        if not remaining:
            return True
        for num in list(remaining):
            new_called = called | {num}
            hr, _ = check_bingo_from_marked(real_layout, new_called, game_id)
            hf, _ = check_bingo_from_marked(fake_layout, new_called, game_id)
            if hr or hf:
                continue
            order.append(num)
            if backtrack(remaining - {num}, new_called):
                return True
            order.pop()
        return False

    if backtrack(set(U), set()):
        return order
    return None


def build_test_co_win_sequence(
    real_layout,
    fake_layout,
    winning_patterns: List[str],
    game_id: int,
) -> Optional[List[int]]:
    """
    Returns ordered list of numbers to call (last element is the shared completing call), or None.
    """
    if not real_layout or not fake_layout:
        return None

    lines_r = _enumerate_line_number_sets(real_layout, winning_patterns)
    lines_f = _enumerate_line_number_sets(fake_layout, winning_patterns)
    if not lines_r or not lines_f:
        return None

    for Sr in lines_r:
        for Sf in lines_f:
            inter = Sr & Sf
            for N in inter:
                U = (Sr | Sf) - {N}
                ob = _try_order_before(U, N, real_layout, fake_layout, game_id) if U else []
                if ob is not None:
                    return ob + [N]
    return None
