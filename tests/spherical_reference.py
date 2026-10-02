"""Independent B-06 real radial differentiation, Euler and period-mean flux."""

from decimal import Decimal, localcontext

from plane_wave_reference import decimal_value, pi, sin_cos


def reference(case, digits=60):
    with localcontext() as context:
        context.prec = digits + 12
        wave = case["wave"]
        rho = decimal_value(wave["density_kg_m3"])
        c = decimal_value(wave["sound_speed_m_s"])
        omega = 2 * pi(digits) * decimal_value(wave["frequency_hz"])
        k, z = omega / c, rho * c
        amplitude = decimal_value(wave["peak_pressure_pa"])
        r_ref = decimal_value(wave["reference_radius_m"])
        pressure, velocity, gradient, intensity = [], [], [], []
        for point in case["coordinates_m"]:
            delta = [decimal_value(x) - decimal_value(s) for x, s in zip(point, wave["center_m"])]
            r = sum(d * d for d in delta).sqrt()
            ns = [d / r for d in delta]
            s, co = sin_cos(k * (r - r_ref) + decimal_value(wave["phase_rad"]), digits)
            p = amplitude * r_ref / r
            pressure.append((p * co, p * s))
            derivatives = [
                (n * (-p * co / r - k * p * s), n * (-p * s / r + k * p * co)) for n in ns
            ]
            gradient.append(derivatives)
            velocity.append(
                [(imag / (omega * rho), -real / (omega * rho)) for real, imag in derivatives]
            )
            intensity.append([amplitude**2 * r_ref**2 * n / (2 * z * r**2) for n in ns])
        scale = amplitude or Decimal(2)
        reactive = 1 + 2 / pi(digits)
        return {
            "pressure": pressure,
            "velocity": velocity,
            "pressure_gradient": gradient,
            "intensity": intensity,
            "scales": {
                "pressure": scale,
                "velocity": scale / z * reactive,
                "pressure_gradient": k * scale * reactive,
                "intensity": scale**2 / (2 * z),
            },
        }
