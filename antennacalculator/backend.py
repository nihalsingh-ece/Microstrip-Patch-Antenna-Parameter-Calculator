import math
import numpy as np

c = 299792458000  # mm/s

class AntennaCalculator:
    """Backend calculations for antenna design"""

    def __init__(self):
        self.current_results = {}

    def calculate_parameters(self, f, e, t, h, Zo, antenna_type, auto_calculate_h=False):
        """Calculate parameters based on antenna type"""
        try:
            f_hz = f * 1e9

            # Auto-calculate h if needed
            if auto_calculate_h:
                h = (0.3 * c) / (2 * math.pi * f_hz * math.sqrt(e))

            # Calculate basic parameters (common to all antenna types)
            W = c / (2 * f_hz * math.sqrt((e + 1) / 2))
            ereff = ((e + 1) / 2) + (((e - 1) / 2) * (1 / math.sqrt(1 + 12 * (h / W))))
            leff = c / (2 * f_hz * math.sqrt(ereff))
            dl = 0.412 * h * (((ereff + 0.3) * ((W / h) + 0.264)) / ((ereff - 0.258) * ((W / h) - 0.8)))
            L = leff - (2 * dl)
            Lg, Wg = L + (6 * h), W + (6 * h)

            results = {
                'f': f,
                'e': e,
                't': t,
                'h': h,
                'Zo': Zo,
                'W': W,
                'L': L,
                'Lg': Lg,
                'Wg': Wg,
                'dl': dl,
                'ereff': ereff,
                'leff': leff,
                'antenna_type': antenna_type
            }

            # Calculate type-specific parameters
            if antenna_type == "Microstrip Patch Antenna (Inset-Fed)":
                Fi = ((10 ** -4) * ((0.001699 * e ** 7) + (0.13761 * e ** 6) - (6.1783 * e ** 5) +
                                    (93.187 * e ** 4) - (682.69 * e ** 3) + (2561.9 * e ** 2) -
                                    (4043 * e) + 6697) * (L / 2)) * 0.83477
                Wf = ((7.48 * h) / (math.e ** (Zo * ((math.sqrt(e + 1.41)) / 87)))) - (1.25 * t)
                Rin = W ** 2 / (1.5 * e)
                Zin = Zo / (1 + (Zo / Rin))
                Γ = (Zin - Zo) / (Zin + Zo)
                S11 = 20 * math.log10(abs(Γ))
                VSWR = (1 + abs(Γ)) / (1 - abs(Γ))

                results.update({
                    'Fi': Fi,
                    'Wf': Wf,
                    'S11': S11,
                    'VSWR': VSWR,
                    'Rin': Rin,
                    'Zin': Zin
                })

            elif antenna_type == "Coaxial Feed Patch Antenna (Beta)":
                Xf = L / (2 * math.sqrt(ereff))
                Yf = W / (3 * math.sqrt(ereff))
                results.update({
                    'Xf': Xf,
                    'Yf': Yf
                })

            elif antenna_type == "Circularly Polarized Antennas (Beta)":
                Q = (c * math.sqrt(ereff)) / (4 * f_hz * h)
                a = L * math.sqrt(1 / (2 * Q))
                results.update({
                    'a': a,
                    'Q': Q
                })

            self.current_results = results
            return results

        except Exception as e:
            raise Exception(f"Calculation error: {str(e)}")

    def _calculate_beamwidth(self, pattern, angles):
        """Calculate 3dB beamwidth from normalized pattern"""
        try:
            # Find half-power points (-3dB = 0.707 of maximum)
            half_power = 0.707

            # Find the main lobe peak (should be around 0/360 degrees)
            peak_idx = np.argmax(pattern)

            # Search for half-power points on either side of peak
            left_idx = None
            right_idx = None

            # Search left from peak
            for i in range(peak_idx, -1, -1):
                if pattern[i] <= half_power:
                    left_idx = i
                    break

            # Search right from peak
            for i in range(peak_idx, len(pattern)):
                if pattern[i] <= half_power:
                    right_idx = i
                    break

            if left_idx is not None and right_idx is not None:
                beamwidth = angles[right_idx] - angles[left_idx]
                return abs(beamwidth)
            else:
                return None

        except:
            return None

    def get_structure_coordinates(self, Fi, Wf, W, L, Lg, Wg, dl):
        """Get coordinates for antenna structure plot"""
        # Ground plane coordinates
        ground_coords = {
            'x': [0, Wg, Wg, 0, 0],
            'y': [0, 0, Lg, Lg, 0]
        }

        # Patch coordinates (main shape)
        Ax, Ay = (Wg - W) / 2, (Lg - L) / 2
        Bx, By = (Wg - 2 * Fi - Wf) / 2, (Lg - L) / 2
        Cx, Cy = (Wg - 2 * Fi - Wf) / 2, (Lg - L) / 2 + Fi
        Dx, Dy = (Wg - Wf) / 2, (Lg - L) / 2 + Fi
        Ex, Ey = (Wg - Wf) / 2, 0
        Fx, Fy = (Wg + Wf) / 2, 0
        Gx, Gy = (Wg + Wf) / 2, (Lg - L) / 2 + Fi
        Hx, Hy = (Wg + Wf) / 2 + Fi, (Lg - L) / 2 + Fi
        Ix, Iy = (Wg + Wf) / 2 + Fi, (Lg - L) / 2
        Jx, Jy = (Wg + W) / 2, (Lg - L) / 2
        Kx, Ky = (Wg + W) / 2, (Lg + L) / 2
        Lx, Ly = (Wg - W) / 2, (Lg + L) / 2

        patch_coords = {
            'x': [Ax, Bx, Cx, Dx, Ex, Fx, Gx, Hx, Ix, Jx, Kx, Lx],
            'y': [Ay, By, Cy, Dy, Ey, Fy, Gy, Hy, Iy, Jy, Ky, Ly]
        }

        # Extended patch coordinates (with dl)
        patch_ext_coords = {
            'x': [Ax, Bx, Cx, Dx, Ex, Fx, Gx, Hx, Ix, Jx, Kx, Lx],
            'y': [Ay - dl, By - dl, Cy - dl, Dy - dl, Ey, Fy, Gy - dl,
                  Hy - dl, Iy - dl, Jy - dl, Ky + dl, Ly + dl]
        }

        return ground_coords, patch_coords, patch_ext_coords