# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def t_prime_end2end(
    t_e2e,
    f,
    t_cpu,
    service_cpu_percentages,
    service_cpu_g_factors,
    service_cpu_t_setups,
    service_cpu_s_factors,
    service_cpu_oo,
    service_cpu_bytes,
    bandwidth_off,
    all_cpu_components,
    unchained_cpu_components,
    chained_cpu_components_ordered,
    debug=False,
    printbottleneck=False,
    ignore_t_dep=False,
    pct_t_dep=100,
):
  def t_prime_cpu():
    a = t_chained()
    b = t_unchained()
    c = t_non_accel()
    v = a + b + c
    if debug:
      print(f"t_prime_cpu = {v} = {a} + {b} + {c}")
    return v

  def t_non_accel():
    set_non_accel = (
        set(all_cpu_components)
        - set(unchained_cpu_components)
        - set(chained_cpu_components_ordered)
    )
    a = sum([t_sub(e) for e in set_non_accel])
    if debug:
      print(f"Non-accel: {set_non_accel}")
      print(f"Ch. Accel: {chained_cpu_components_ordered}")
      print(f"UCh. Accel: {unchained_cpu_components}")
      print(f"t_non_accel = {a}")
    return a

  def t_chained():
    if len(chained_cpu_components_ordered) == 0:
      return 0
    else:
      a = max([t_pen(e) for e in chained_cpu_components_ordered])
      c = [t_sub(e) / s_sub(e) for e in chained_cpu_components_ordered]
      b = max(c)
      if printbottleneck:
        print(f"Max:{b} Which:{chained_cpu_components_ordered[c.index(b)]}")
      if debug:
        print(f"t_chained = {a + b}")
      return a + b

  def t_unchained():
    a = sum([g_sub(e) * t_ss(e) for e in unchained_cpu_components])
    v = max([a] + [t_ss(e) for e in unchained_cpu_components])
    if debug:
      print(f"t_unchained = {v}")
    return v

  def t_ss(e):
    v = (t_sub(e) / s_sub(e)) + t_pen(e)
    if debug:
      print(f"t_ss({e}) = {v} = {t_sub(e)} / {s_sub(e)} + {t_pen(e)}")
    return v

  def g_sub(e):
    if not e in service_cpu_g_factors:
      print(f"{e} not in cpu g factors. Is this expected?")
    v = service_cpu_g_factors.get(e, 1)
    if debug:
      print(f"g({e}) = {v}")
    return v

  def t_sub(e):
    if e in service_cpu_percentages:
      v = (t_cpu * service_cpu_percentages[e]) / 100
    else:
      print(f"{e} not in cpu percentages. Is this expected?")
      v = 0
    if debug:
      if e in service_cpu_percentages:
        print(
            f"t_sub({e}) = {v} = {t_cpu} * {service_cpu_percentages[e] / 100}"
        )
    return v

  def t_pen(e):
    if not e in service_cpu_t_setups:
      print(f"{e} not in cpu t_setups. Is this expected?")
    v = service_cpu_t_setups.get(e, 0)
    if oo(e):
      v += 2 * service_cpu_bytes[e] / bandwidth_off
    if debug:
      print(f"t_pen({e}) = {v}")
    return v

  def oo(e):
    if not e in service_cpu_oo:
      print(f"{e} not in cpu oos. Is this expected?")
    v = service_cpu_oo.get(e, 0)
    if debug:
      print(f"oo({e}) = {v}")
    return v

  def s_sub(e):
    if not e in service_cpu_s_factors:
      print(f"{e} not in cpu s factors. Is this expected?")
    v = service_cpu_s_factors.get(e, 1)
    if debug:
      print(f"s({e}) = {v}")
    return v

  # since we know t_cpu >= t_dep
  def t_dep():
    if not ignore_t_dep:
      v = (t_e2e - t_cpu) / f
      v = (v * pct_t_dep) / 100
      return v
    else:
      return 0

  v = t_prime_cpu() + t_dep() - (1 - f) * min(t_cpu, t_dep())
  if debug:
    print(f"t_cpu = {t_cpu}")
    print(f"f = {f}")
    print(f"t_prime_e2e(*) = {v}")
    print(f"t_e2e = {t_e2e}")
  return t_e2e / v
