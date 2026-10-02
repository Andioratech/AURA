"""B-05 real-sinusoid/Euler oracle and independent period-integral flux."""

from decimal import Decimal, localcontext

from plane_wave_reference import decimal_value, pi, sin_cos


def reference(case, digits=60):
    with localcontext() as context:
        context.prec = digits + 12
        waves = [case["first"], case["second"]]
        rho = decimal_value(waves[0]["density_kg_m3"])
        speed = decimal_value(waves[0]["sound_speed_m_s"])
        omega = 2 * pi(digits) * decimal_value(waves[0]["frequency_hz"])
        k = omega / speed
        impedance = rho * speed
        amplitudes = [decimal_value(w["peak_pressure_pa"]) for w in waves]
        directions = [[decimal_value(n) for n in w["direction"]] for w in waves]
        pressure, gradient, velocity, intensity = [], [], [], []
        for point in case["coordinates_m"]:
            angles = [
                k
                * sum(
                    n * (decimal_value(x) - decimal_value(r))
                    for n, x, r in zip(ns, point, w["reference_m"], strict=True)
                )
                + decimal_value(w["phase_rad"])
                for w, ns in zip(waves, directions, strict=True)
            ]
            trigs = [sin_cos(angle, digits) for angle in angles]
            pressure.append(
                (
                    sum(a * c for a, (s, c) in zip(amplitudes, trigs, strict=True)),
                    sum(a * s for a, (s, c) in zip(amplitudes, trigs, strict=True)),
                )
            )
            derivatives = [
                (
                    -k
                    * sum(
                        a * n[j] * s
                        for a, n, (s, c) in zip(amplitudes, directions, trigs, strict=True)
                    ),
                    k
                    * sum(
                        a * n[j] * c
                        for a, n, (s, c) in zip(amplitudes, directions, trigs, strict=True)
                    ),
                )
                for j in range(3)
            ]
            gradient.append(derivatives)
            velocity.append(
                [(imag / (omega * rho), -real / (omega * rho)) for real, imag in derivatives]
            )
            cosine_difference = sin_cos(angles[0] - angles[1], digits)[1]
            a, b = amplitudes
            n, m = directions
            intensity.append(
                [
                    (a * a * n[j] + b * b * m[j] + a * b * (n[j] + m[j]) * cosine_difference)
                    / (2 * impedance)
                    for j in range(3)
                ]
            )
        scale = sum(amplitudes) or Decimal(2)
        return {
            "pressure": pressure,
            "velocity": velocity,
            "pressure_gradient": gradient,
            "intensity": intensity,
            "scales": {
                "pressure": scale,
                "velocity": scale / impedance,
                "pressure_gradient": k * scale,
                "intensity": scale**2 / (2 * impedance),
            },
        }
