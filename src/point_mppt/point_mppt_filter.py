from typing import Optional

from ..point.point_filter import GetPointFilter


class AddPanelFilter(GetPointFilter):
    parent: Optional[int] = 0
    is_clone_from_last: Optional[bool] = False
    num_of_panels: Optional[int] = 0


class AddStringFilter(AddPanelFilter):
    num_of_strings: Optional[int] = 0


class AddMPPTFilter(AddStringFilter):
    num_of_mppt: Optional[int] = 0

