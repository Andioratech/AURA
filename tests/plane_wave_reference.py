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


def reference(case, digits=60):
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
