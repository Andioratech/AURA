"""Independent B-04 combined trigonometric identities; no production imports."""

from decimal import Decimal, localcontext

from plane_wave_reference import decimal_value, pi, sin_cos


def reference(case, digits=60):
    with localcontext() as context:
        context.prec = digits + 12
        first, second = case["forward"], case["backward"]
        rho = decimal_value(first["density_kg_m3"])
        speed = decimal_value(first["sound_speed_m_s"])
        k = 2 * pi(digits) * decimal_value(first["frequency_hz"]) / speed
        impedance = rho * speed
        n = [decimal_value(x) for x in first["direction"]]
        a, b = (decimal_value(w["peak_pressure_pa"]) for w in (first, second))
        alpha = decimal_value(first["phase_rad"]) - k * sum(
            x * decimal_value(r) for x, r in zip(n, first["reference_m"], strict=True)
        )
        beta = decimal_value(second["phase_rad"]) + k * sum(
            x * decimal_value(r) for x, r in zip(n, second["reference_m"], strict=True)
        )
        sine_delta, cosine_delta = sin_cos((alpha + beta) / 2, digits)

        def rotate(real, imag):
            return (
                real * cosine_delta - imag * sine_delta,
                real * sine_delta + imag * cosine_delta,
            )

        pressure, velocity, gradient, intensity = [], [], [], []
        for point in case["coordinates_m"]:
            xi = k * sum(x * decimal_value(r) for x, r in zip(n, point, strict=True))
            sine, cosine = sin_cos(xi + (alpha - beta) / 2, digits)
            pressure.append(rotate((a + b) * cosine, (a - b) * sine))
            velocity.append(
                [
                    rotate(x * (a - b) * cosine / impedance, x * (a + b) * sine / impedance)
                    for x in n
                ]
            )
            gradient.append([rotate(-x * k * (a + b) * sine, x * k * (a - b) * cosine) for x in n])
            intensity.append([x * (a * a - b * b) / (2 * impedance) for x in n])
        scale = a + b or Decimal(2)
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
