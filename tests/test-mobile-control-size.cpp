// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/shared/GalaxyPadControlSize.h"
#include <cassert>
#include <limits>
int main() {
  using namespace galaxypad;
  // With a bottom gutter, anchor the complete face-button cluster to the safe
  // edge, not merely one gutter-height lower (which still covers Galaxy's HUD).
  assert(bottomActionShift(834, 748, 722) == 100);
  assert(bottomActionShift(834, 834, 722) == 0);
  assert(bottomActionShift(834, 748, 830) == 0);
  assert(bottomActionShift(834, std::numeric_limits<double>::quiet_NaN(), 722) == 0);
  for (int bottom = 0; bottom <= 822; ++bottom)
    assert(bottom + bottomActionShift(834, 748, bottom) == 822);
  assert(bottomLetterboxShift(800, 700, 690) == 98);
  assert(bottomLetterboxShift(800, 780, 690) == 20);
  assert(bottomLetterboxShift(800, 800, 690) == 0);
  assert(bottomLetterboxShift(800, 700, 795) == 0);
  assert(bottomLetterboxShift(800, std::numeric_limits<double>::quiet_NaN(), 690) == 0);
  for (int viewport = 0; viewport <= 900; viewport += 10)
    for (int bottom = 0; bottom <= 800; bottom += 10) {
      double shift = bottomLetterboxShift(800, viewport, bottom);
      assert(shift >= 0 && shift <= std::max(0, 800-viewport));
      if (bottom <= 788) assert(bottom+shift <= 788);
    }
  assert(controlScale(std::numeric_limits<double>::quiet_NaN()) == 1);
  assert(controlScale(-5) == 0.7 && controlScale(50) == 1.8);
  assert(controlSide(44, 0.7, 300, 44) == 44);
  assert(controlSide(66, 1, 300, 44) == 66);
  assert(controlSide(156, 1.8, 200, 84) == 200);
  assert(controlSide(156, 1, 0, 84) == 0);
  for (int available = 1; available <= 1200; ++available)
    for (int scale = -20; scale <= 40; ++scale) {
      double result = controlSide(66, scale/10.0, available, 44);
      assert(std::isfinite(result) && result <= available);
      assert(result >= std::min(44, available));
    }
}
