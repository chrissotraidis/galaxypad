// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <cmath>

namespace galaxypad {
inline double bottomActionShift(double safeBottom, double viewportBottom, double controlsBottom) {
  if (!std::isfinite(safeBottom) || !std::isfinite(viewportBottom) ||
      !std::isfinite(controlsBottom) || viewportBottom >= safeBottom) return 0;
  return std::max(0.0, safeBottom - controlsBottom - 12.0);
}
inline double bottomLetterboxShift(double safeBottom, double viewportBottom, double controlsBottom) {
  if (!std::isfinite(safeBottom) || !std::isfinite(viewportBottom) ||
      !std::isfinite(controlsBottom)) return 0;
  return std::max(0.0, std::min(safeBottom - viewportBottom,
                                safeBottom - controlsBottom - 12.0));
}
inline double controlScale(double scale) {
  return std::isfinite(scale) ? std::clamp(scale, 0.7, 1.8) : 1.0;
}
inline double controlSide(double base, double scale, double available, double minimum) {
  if (!std::isfinite(available) || available <= 0) return 0;
  return std::min(available, std::max(minimum, base * controlScale(scale)));
}
}
