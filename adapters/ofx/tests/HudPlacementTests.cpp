#include "../src/HudPlacement.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>

int main(int argc, char** argv) {
 using namespace pmhud;
 bool passed = true;
 const auto check = [&passed](bool condition, const char* name) {
  if (!condition) {
   std::cerr << "HUD placement FAIL: " << name << '\n';
   passed = false;
  }
 };

 const auto full = placeHud(1280, 720, {0, 0, 1280, 720});
 check(full.visible && full.bounds.x2 == 1280, "full viewport");
 const auto zoom = placeHud(1280, 720, {590, 310, 690, 410});
 check(zoom.visible && zoom.bounds.x1 == 0 && zoom.bounds.x2 == 1280, "zoomed image");
 const auto portrait = placeHud(650, 560, {200, 0, 450, 560});
 check(portrait.visible && portrait.bounds.x1 == 0, "portrait viewport");
 const auto crop = placeHud(1280, 720, {-100, -100, 1800, 900});
 check(crop.visible && crop.bounds.x1 == 0 && crop.bounds.y2 == 720, "cropped image");
 const auto off = placeHud(1280, 720, {2000, 2000, 2100, 2100});
 check(off.visible && off.bounds.x1 == 0, "offscreen image");
 check(!placeHud(399, 720, {0, 0, 399, 720}).visible, "viewport too narrow");
 check(!placeHud(1280, 307, {0, 0, 1280, 307}).visible, "viewport too short");
 const double n = std::numeric_limits<double>::quiet_NaN();
 const auto invalid = placeHud(1280, 720, {n, n, n, n});
 check(invalid.visible, "non-finite image bounds");
 if (!passed) return EXIT_FAILURE;

 if (argc > 1) {
  std::ofstream out(argv[1]);
  if (!out) {
   std::cerr << "HUD placement FAIL: cannot open report: " << argv[1] << '\n';
   return EXIT_FAILURE;
  }
  out << "{\"status\":\"PASS\",\"cases\":8,\"Host_verified\":false}\n";
  out.close(); // Checks below include write errors and the buffered flush on close.
  if (!out) {
   std::cerr << "HUD placement FAIL: cannot write or close report: " << argv[1] << '\n';
   return EXIT_FAILURE;
  }
 }
 std::cout << "HUD placement PASS: 8 cases; Host not tested\n";
 return EXIT_SUCCESS;
}
