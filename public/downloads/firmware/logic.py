"""Pure state helpers, shared by firmware and desktop tests."""
PHYSICAL_TO_LOGICAL = {1:0, 2:1, 4:2, 5:3, 6:4, 7:5, 8:6, 9:7, 10:8, 11:9, 13:10, 14:10, 15:11}

class KeyState:
    """Merge the two physical wide-key switches; avoid duplicate/stuck HID keys."""
    def __init__(self):
        self.physical = set()
    def update(self, physical, down):
        logical = PHYSICAL_TO_LOGICAL.get(physical)
        if logical is None:
            return None
        before = any(PHYSICAL_TO_LOGICAL[p] == logical for p in self.physical)
        if down:
            self.physical.add(physical)
        else:
            self.physical.discard(physical)
        after = any(PHYSICAL_TO_LOGICAL[p] == logical for p in self.physical)
        return (logical, after) if before != after else None

def direction(x, y, center, previous=None, enter=7000, leave=4500):
    dx=x-center[0]; dy=y-center[1]
    magnitude=max(abs(dx),abs(dy))
    if magnitude < (leave if previous else enter):
        return None
    return ('right' if dx>0 else 'left') if abs(dx)>abs(dy) else ('up' if dy>0 else 'down')

def rgbw(value):
    if not isinstance(value, (list,tuple)) or len(value) not in (3,4):
        raise ValueError('Use three or four color channels')
    if any(not isinstance(v,int) or v<0 or v>255 for v in value):
        raise ValueError('Color channel must be integer 0..255')
    return tuple(value)+(0,) if len(value)==3 else tuple(value)
