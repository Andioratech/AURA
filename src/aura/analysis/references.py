"""Independent Decimal reference for B-03; no aura or binary trig imports.

Scalar (real, imaginary) pairs keep this route separate from production complex
arithmetic. This is a test oracle, not a second validated physical model.
"""

from decimal import ROUND_HALF_EVEN, Decimal, localcontext


def decimal_value(value):
    """Interpret intended fixture decimal spelling, not a previously rounded float."""
    return Decimal(str(value))


def _atan_inverse(denominator, digits):
    x = Decimal(1) / denominator
    power = x
    total = power
    for index in range(1, 256):
        power = -power * x * x
        term = power / (2 * index + 1)
        total += term
        if abs(term) < Decimal(10) ** (-digits - 8):
            return total
    raise AssertionError("Arctangent reference exceeded its frozen iteration cap")


def pi(digits):
    with localcontext() as context:
        context.prec = digits + 12
        context.rounding = ROUND_HALF_EVEN
        return 16 * _atan_inverse(Decimal(5), digits) - 4 * _atan_inverse(Decimal(239), digits)


def sin_cos(angle, digits):
    with localcontext() as context:
        context.prec = digits + 12
        context.rounding = ROUND_HALF_EVEN
        sine, cosine = angle, Decimal(1)
        sin_term, cos_term = angle, Decimal(1)
        square = angle * angle
        for index in range(1, 256):
            sin_term = -sin_term * square / ((2 * index) * (2 * index + 1))
            cos_term = -cos_term * square / ((2 * index - 1) * (2 * index))
            sine += sin_term
            cosine += cos_term
            if max(abs(sin_term), abs(cos_term)) < Decimal(10) ** (-digits - 8):
                return sine, cosine
    raise AssertionError("Trigonometric reference exceeded its frozen iteration cap")


def reference_b03(case, digits=60):
    """Pressure and independently differentiated real-sinusoid components in SI."""
    with localcontext() as context:
        context.prec = digits + 12
        context.rounding = ROUND_HALF_EVEN
        wave = case["wave"]
        rho = decimal_value(wave["density_kg_m3"])
        speed = decimal_value(wave["sound_speed_m_s"])
        frequency = decimal_value(wave["frequency_hz"])
        amplitude = decimal_value(wave["peak_pressure_pa"])
        phase = decimal_value(wave["phase_rad"])
        direction = [decimal_value(x) for x in wave["direction"]]
        origin = [decimal_value(x) for x in wave["reference_m"]]
        omega = 2 * pi(digits) * frequency
        k = omega / speed
        pressure, velocity, gradient, intensity = [], [], [], []
        for point in case["coordinates_m"]:
            distance = sum(
                n * (decimal_value(x) - ref) for n, x, ref in zip(direction, point, origin)
            )
            sine, cosine = sin_cos(k * distance + phase, digits)
            pressure.append((amplitude * cosine, amplitude * sine))
            derivatives = [
                (-amplitude * k * n * sine, amplitude * k * n * cosine) for n in direction
            ]
            gradient.append(derivatives)
            # Solve the two real Euler-component equations from independently
            # differentiated sinusoids, rather than reuse p/(rho*c) in the oracle.
            velocity.append(
                [(imag / (omega * rho), -real / (omega * rho)) for real, imag in derivatives]
            )
            # Exact one-period cosine-squared integral: independent of computed p*v.
            intensity.append([n * amplitude**2 / (2 * rho * speed) for n in direction])
        scale = Decimal(2)  # Frozen nonzero B-03 normalization, including zero drive.
        return {
            "pressure": pressure,
            "velocity": velocity,
            "pressure_gradient": gradient,
            "intensity": intensity,
            "scales": {
                "pressure": scale,
                "velocity": scale / (rho * speed),
                "pressure_gradient": k * scale,
                "intensity": scale**2 / (2 * rho * speed),
            },
        }


def pairs_as_complex(rows):
    return [complex(float(real), float(imag)) for real, imag in rows]


def reference_b04(case, digits=60):
    """Independent B-04 combined trigonometric identities; no production imports."""
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
            gradient.append(
                [
                    rotate(-x * k * (a + b) * sine, x * k * (a - b) * cosine)
                    for x in n
                ]
            )
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


def reference_b05(case, digits=60):
    """B-05 real-sinusoid/Euler oracle and independent period-integral flux."""
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


def reference_b06(case, digits=60):
    """Independent real radial differentiation, Euler and period-mean flux."""
    with localcontext() as context:
        context.prec = digits + 12
        wave = case["wave"]
        rho = decimal_value(wave["density_kg_m3"])
        speed = decimal_value(wave["sound_speed_m_s"])
        omega = 2 * pi(digits) * decimal_value(wave["frequency_hz"])
        k, impedance = omega / speed, rho * speed
        amplitude = decimal_value(wave["peak_pressure_pa"])
        reference_radius = decimal_value(wave["reference_radius_m"])
        center = [decimal_value(value) for value in wave["center_m"]]
        pressure, velocity, gradient, intensity = [], [], [], []
        for point in case["coordinates_m"]:
            delta = [decimal_value(value) - origin for value, origin in zip(point, center, strict=True)]
            radius = sum(value * value for value in delta).sqrt()
            direction = [value / radius for value in delta]
            sine, cosine = sin_cos(
                k * (radius - reference_radius) + decimal_value(wave["phase_rad"]), digits
            )
            local_pressure = amplitude * reference_radius / radius
            pressure.append((local_pressure * cosine, local_pressure * sine))
            derivatives = [
                (
                    normal * (-local_pressure * cosine / radius - k * local_pressure * sine),
                    normal * (-local_pressure * sine / radius + k * local_pressure * cosine),
                )
                for normal in direction
            ]
            gradient.append(derivatives)
            velocity.append([
                (imaginary / (omega * rho), -real / (omega * rho))
                for real, imaginary in derivatives
            ])
            intensity.append([
                amplitude**2 * reference_radius**2 * normal / (2 * impedance * radius**2)
                for normal in direction
            ])
        scale = amplitude or Decimal(2)
        reactive = 1 + 2 / pi(digits)
        return {
            "pressure": pressure,
            "velocity": velocity,
            "pressure_gradient": gradient,
            "intensity": intensity,
            "scales": {
                "pressure": scale,
                "velocity": scale / impedance * reactive,
                "pressure_gradient": k * scale * reactive,
                "intensity": scale**2 / (2 * impedance),
            },
        }
