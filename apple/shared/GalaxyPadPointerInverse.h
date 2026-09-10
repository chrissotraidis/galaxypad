// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <cmath>
#include <optional>

namespace galaxypad {
struct PointerPoint { float x, y; };
// Camera quantization alone is about .00222 normalized steps at scale 2.272727.
// Allow 1.25 logical pixels at width832, including small sensor-roll effects.
inline constexpr float PointerInverseTolerance=.0015f;

// Both domains use normalized, top-left coordinates. The caller supplies a
// verified forward model for the current configuration. This solves a settled
// position only; it cannot establish guest readiness, filtering or tap consent.
// At most 75 model evaluations, no allocation or unbounded convergence loop.
template<class Forward>
std::optional<PointerPoint> InvertPointer(PointerPoint target, Forward forward) {
  auto finite=[](PointerPoint p) { return std::isfinite(p.x) && std::isfinite(p.y); };
  if (!finite(target) || target.x<0 || target.x>1 || target.y<0 || target.y>1)
    return std::nullopt;
  PointerPoint input=target;
  constexpr float h=.01f;
  for (unsigned iteration=0;iteration<10;++iteration) {
    auto value=forward(input);
    if (!value || !finite(*value)) return std::nullopt;
    const float ex=target.x-value->x, ey=target.y-value->y;
    if (std::max(std::abs(ex),std::abs(ey))<=PointerInverseTolerance) return input;
    float xl=std::max(0.f,input.x-h), xr=std::min(1.f,input.x+h);
    float yl=std::max(0.f,input.y-h), yr=std::min(1.f,input.y+h);
    auto left=forward(PointerPoint{xl,input.y}),right=forward(PointerPoint{xr,input.y});
    auto up=forward(PointerPoint{input.x,yl}),down=forward(PointerPoint{input.x,yr});
    if (!left || !right || !up || !down || !finite(*left) || !finite(*right) ||
        !finite(*up) || !finite(*down)) return std::nullopt;
    const float a=(right->x-left->x)/(xr-xl), b=(down->x-up->x)/(yr-yl);
    const float c=(right->y-left->y)/(xr-xl), d=(down->y-up->y)/(yr-yl);
    const float determinant=a*d-b*c;
    if (!std::isfinite(determinant) || std::abs(determinant)<1e-6f) return std::nullopt;
    const float dx=(d*ex-b*ey)/determinant, dy=(a*ey-c*ex)/determinant;
    if (!std::isfinite(dx) || !std::isfinite(dy)) return std::nullopt;
    input.x=std::clamp(input.x+std::clamp(dx,-.25f,.25f),0.f,1.f);
    input.y=std::clamp(input.y+std::clamp(dy,-.25f,.25f),0.f,1.f);
  }
  // Integer camera pixels can make Newton oscillate across a discontinuity.
  // Check a fixed sub-pixel neighborhood, retaining the same error threshold.
  for(int x=-2;x<=2;++x) for(int y=-2;y<=2;++y) {
    PointerPoint candidate{std::clamp(input.x+x*.001f,0.f,1.f),
                           std::clamp(input.y+y*.001f,0.f,1.f)};
    auto value=forward(candidate);
    if(value && finite(*value) &&
       std::max(std::abs(target.x-value->x),std::abs(target.y-value->y))<=PointerInverseTolerance)
      return candidate;
  }
  return std::nullopt; // never return an unverified last iterate
}
} // namespace galaxypad
