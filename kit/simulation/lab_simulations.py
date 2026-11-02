"""Reproducible educational simulations for Omar Zid, not physical measurements.

Run with Python 3 and Pillow. All model constants are declared below. A fixed
seed makes CSVs and reported numbers reproducible; truth and observed values
are saved separately. No NXT brick, motor or sensor was used for these results.
"""
from __future__ import annotations

import csv
import json
import math
import random
import statistics as st
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "labs"
FIG = DATA / "figures"
CONTENT = ROOT / "data" / "report_content" / "lab_content.json"
SEED = 20261014
D_MM = 56.0
TRACK_MM = 120.0
RNG = random.Random(SEED)
CHECKS = []
FONT_PATH = Path("C:/Windows/Fonts/arial.ttf")


def font(size=22):
    return ImageFont.truetype(str(FONT_PATH), size) if FONT_PATH.exists() else ImageFont.load_default()


def check(name, ok, detail=""):
    CHECKS.append({"check": name, "passed": bool(ok), "detail": str(detail)})
    if not ok:
        raise AssertionError(f"{name}: {detail}")


def csv_write(name, rows):
    path = DATA / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def mean(xs):
    return st.mean(xs)


def sd(xs):
    return st.stdev(xs) if len(xs) > 1 else 0.0


def fmt(x, digits=2):
    return f"{x:.{digits}f}"


def linear_fit(xs, ys):
    mx, my = mean(xs), mean(ys)
    sxx = sum((x-mx)**2 for x in xs)
    a = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sxx
    b = my-a*mx
    residuals = [y-a*x-b for x, y in zip(xs, ys)]
    sigma = math.sqrt(sum(e*e for e in residuals)/(len(xs)-2))
    return a, b, sigma, mx, sxx


def section(heading, paragraphs=None, headers=None, rows=None, calculations=None, figure=None, caption=None):
    obj = {"heading": heading, "paragraphs": paragraphs or []}
    if headers:
        obj["table"] = {"headers": headers, "rows": rows}
    if calculations:
        obj["calculations"] = calculations
    if figure:
        obj["figure"] = str(figure)
        obj["caption"] = caption
    return obj


def plot_xy(name, title, series, xlabel, ylabel, xlim=None, ylim=None):
    """Publication-size raster plot drawn with Pillow, with explicit units."""
    im = Image.new("RGB", (1400, 830), "white")
    draw = ImageDraw.Draw(im)
    left, top, right, bottom = 135, 158, 1330, 660
    xs = [x for item in series for x, y in item[1]]
    ys = [y for item in series for x, y in item[1]]
    xlo, xhi = xlim or (min(xs), max(xs))
    ylo, yhi = ylim or (min(0, min(ys)), max(ys)*1.08)
    if xhi == xlo: xhi += 1
    if yhi == ylo: yhi += 1
    def p(x, y):
        return (left+(x-xlo)/(xhi-xlo)*(right-left), bottom-(y-ylo)/(yhi-ylo)*(bottom-top))
    draw.text((left, 35), title, font=font(32), fill="#14213d")
    draw.text((left, 83), "SIMULATED DATA  |  Omar Zid  |  seed 20261014", font=font(20), fill="#667085")
    for k in range(6):
        xv = xlo+(xhi-xlo)*k/5
        yv = ylo+(yhi-ylo)*k/5
        xp, _ = p(xv, ylo)
        _, yp = p(xlo, yv)
        draw.line((xp, top, xp, bottom), fill="#e7ebf0", width=2)
        draw.line((left, yp, right, yp), fill="#e7ebf0", width=2)
        draw.text((xp-20, bottom+12), fmt(xv, 0 if abs(xhi)>20 else 2), fill="#344054", font=font(20))
        draw.text((left-95, yp-12), fmt(yv, 0 if abs(yhi)>20 else 2), fill="#344054", font=font(20))
    draw.line((left, top, left, bottom, right, bottom), fill="#344054", width=3)
    colors = ["#2563eb", "#dc2626", "#059669", "#7c3aed", "#d97706", "#1e293b"]
    for idx, (label, points) in enumerate(series):
        color = colors[idx % len(colors)]
        pts = [p(x,y) for x,y in points]
        if len(pts)>1: draw.line(pts, fill=color, width=4)
        for xp,yp in pts:
            draw.ellipse((xp-4,yp-4,xp+4,yp+4), fill=color)
        lx = left+(idx%3)*390
        ly = 744+(idx//3)*30
        draw.line((lx,ly+10,lx+32,ly+10), fill=color, width=5)
        draw.text((lx+42,ly-2), label, fill="#344054", font=font(20))
    draw.text((left+410, bottom+48), xlabel, fill="#14213d", font=font(24))
    draw.text((left, top-32), ylabel, fill="#14213d", font=font(22))
    path=FIG/name
    im.save(path)
    return path


def motor_simulation():
    # Assumed sensor model: 1 degree output quantization, scale 1.003, bias 0.65.
    # External simulated angle fixture is independent: 0.5 degree quantization
    # and Gaussian sigma=0.35 degree; it is not the tacho reading copied twice.
    cal=[]
    for angle in (-720,-360,-90,0,90,360,720):
        for trial in range(1,6):
            tacho=round(1.003*angle+0.65+RNG.gauss(0,0.24))
            external=round((angle+RNG.gauss(0,0.35))*2)/2
            cal.append({"nominal_fixture_deg":angle,"trial":trial,"truth_deg":angle,
                        "tacho_raw_deg":tacho,"external_observed_deg":external})
    a,b,cal_sigma,mx,sxx=linear_fit([r["external_observed_deg"] for r in cal],[r["tacho_raw_deg"] for r in cal])
    csv_write("motor_calibration.csv",cal)
    rows=[]
    summaries=[]
    for angle in (45,450,650,-450):
        for power in (30,50,80):
            group=[]
            for trial in range(1,6):
                direction=1 if angle>0 else -1
                truth=angle+direction*(0.12+0.012*power)+RNG.gauss(0,0.12+0.007*power)
                raw=round(1.003*truth+0.65+RNG.gauss(0,0.24))
                ext=round((truth+RNG.gauss(0,0.35))*2)/2
                corrected=(raw-b)/a
                # Motion duration includes an assumed acceleration/brake allowance.
                duration=round((abs(truth)/(5.6*power)+0.15+0.0015*power+RNG.gauss(0,0.008))*1000)/1000
                row={"command_deg":angle,"power_pct":power,"trial":trial,"truth_shaft_deg":round(truth,6),
                     "tacho_raw_deg":raw,"tacho_calibrated_deg":round(corrected,6),
                     "external_observed_deg":ext,"command_error_external_deg":round(ext-angle,6),
                     "tacho_vs_external_error_deg":round(corrected-ext,6),
                     "duration_s":duration,"average_speed_deg_s":round(abs(ext)/duration,6),
                     "nominal_wheel_distance_mm":round(math.pi*D_MM*ext/360,6)}
                group.append(row); rows.append(row)
            vals=[r["external_observed_deg"] for r in group]
            tach=[r["tacho_calibrated_deg"] for r in group]
            external_type_b=math.sqrt(0.35**2+0.5**2/12)
            u=math.sqrt(sd(vals)**2/5+external_type_b**2)
            summary={"command_deg":angle,"power_pct":power,"n":5,"mean_external_deg":mean(vals),
                     "sd_external_deg":sd(vals),"mean_calibrated_deg":mean(tach),"bias_deg":mean(vals)-angle,
                     "relative_error_pct":100*(mean(vals)-angle)/abs(angle),
                     "expanded_uncertainty_deg":2*u,"mean_duration_s":mean([r["duration_s"] for r in group])}
            summaries.append(summary)
    csv_write("motor_trials.csv",rows)
    csv_write("motor_summary.csv",summaries)
    resets=[
        {"event":"Initial","shaft_deg":0,"tacho_count_deg":0,"program_rotation_deg":0},
        {"event":"Relative move +450","shaft_deg":450,"tacho_count_deg":450,"program_rotation_deg":450},
        {"event":"ResetTachoCount only","shaft_deg":450,"tacho_count_deg":0,"program_rotation_deg":450},
        {"event":"Relative move -45 (no automatic reset)","shaft_deg":405,"tacho_count_deg":-45,"program_rotation_deg":405},
        {"event":"ResetRotationCount only","shaft_deg":405,"tacho_count_deg":-45,"program_rotation_deg":0},
        {"event":"Relative move +650 (no automatic reset)","shaft_deg":1055,"tacho_count_deg":605,"program_rotation_deg":650},
    ]
    csv_write("motor_counter_reset_trace.csv",resets)
    # These are API semantics demonstrations, not claims about a RotateMotor
    # implementation's own internally requested resets.
    check("Motor test coverage",len(rows)==60)
    check("Independent-angle observations exist",any(r["tacho_raw_deg"]!=r["external_observed_deg"] for r in rows))
    check("Calibration recovers injected gain",abs(a-1.003)<0.002,f"gain={a:.7f}")
    check("Negative command reverses direction",all(r["truth_shaft_deg"]<0 for r in rows if r["command_deg"]<0))
    check("Counter reset preserves physical shaft",resets[2]["shaft_deg"]==resets[1]["shaft_deg"])
    check("Wheel distance dimensional conversion",abs(math.pi*D_MM*360/360-math.pi*D_MM)<1e-12)
    figure=plot_xy("motor_error.png","Motor positioning: independent simulated shaft measurements",
                   [(f"Power {p}%",[(s["command_deg"],s["bias_deg"]) for s in sorted(summaries,key=lambda r:r["command_deg"]) if s["power_pct"]==p]) for p in (30,50,80)],
                   "Commanded shaft angle (degrees)","Mean signed command error (degrees)",ylim=(-2.0,2.0))
    table=[[str(s["command_deg"]),str(s["power_pct"]),fmt(s["mean_external_deg"]),fmt(s["sd_external_deg"]),fmt(s["bias_deg"]),fmt(s["mean_duration_s"],3)] for s in summaries]
    worst=max(summaries,key=lambda s:abs(s["bias_deg"]))
    sample=next(s for s in summaries if s["command_deg"]==450 and s["power_pct"]==50)
    report={"id":"report_1","title":"Report 1 — Exploring motors","source":"Screenshot_2.png; __NXC_tutorial.pdf, pp. 31–34",
      "summary":f"Omar Zid | Reproducible simulation | 60 test trials. Largest mean signed angle error: {worst['bias_deg']:.2f}° at {worst['command_deg']}° and power {worst['power_pct']}%. No physical experiment is claimed.",
      "sections":[
        section("1. Aim and measurement plan",[
          "The assignment asks for a program that displays the current motor-shaft position, checks commands of 45°, 450° and 650°, and investigates counter resets. A negative command and three powers are added to test direction and the effect of speed. The supplied tutorial explains limited-angle movement, braking and feedback regulation.",
          "One motor represents a wheel-driven NXT system. Each angle/power combination has five simulated repetitions from a reset zero. An independent angle fixture provides the reference observation. Command angle, ideal simulator truth, integer tacho observation and external observation are stored in separate columns so agreement of two tacho-based values cannot masquerade as independent verification.",
          "These are software-generated observations. The model tests calculation, logging and control logic, while the actual brick, loading, battery condition, friction and firmware behavior still require a hardware check. All numerical precision and uncertainty assumptions below belong to this model." ]),
        section("2. Declared model and calibration",[
          "Geometry: wheel diameter D = 56 mm and wheel-centre track B = 120 mm are assumed construction values. Shaft angle is unwrapped; 450° and 650° represent more than one revolution. A power value is a control setting, not a measured angular velocity.",
          "Injected tacho relation: raw = round(1.003 × true angle + 0.65° + noise), noise standard deviation 0.24°. The independent fixture has 0.35° noise and a 0.5° reporting step. The assumed tacho output step is 1°; neither step proves the physical hardware's accuracy. Calibration uses 35 independent readings at seven reference positions from −720° to +720°.",
          f"Least-squares calibration gave raw = {a:.7f} × external + {b:.5f}°. The residual standard deviation was {cal_sigma:.3f}°. Apply θcal = (raw − {b:.5f})/{a:.7f}. The commanded angles are not used as the calibration response, preventing command error from being calibrated away.",
          "Position truth includes a small power-dependent overshoot: signed mean increment 0.12° + 0.012° × power, plus trial noise σ = 0.12° + 0.007° × power. Motion time is |θ|/(5.6 × power) + 0.15 + 0.0015 × power seconds, plus 0.008 s noise, rounded to 1 ms. These constants are chosen for an illustrative simulation, not fitted to a real motor." ]),
        section("3. Results: angle, repeatability and motion time",[
          "The reference mean is the average of five external observations. The signed error is mean reference − commanded angle. Sample standard deviation describes trial repeatability; it does not remove a systematic offset. Expanded uncertainty U with coverage factor k = 2 is calculated below and retained for every condition in motor_summary.csv.",
          "Higher power shortened the modeled motion duration and generally increased overshoot and scatter. A small 45° command can have a noticeably larger percentage error than a 650° command even when the absolute error is similar. Thus angle error and time must both be reported." ],
          ["Command (°)","Power (%)","Ref. mean (°)","s (°)","Error (°)","Time (s)"],table,
          figure=figure,caption="Mean command errors use the independent reference, not the calibrated tacho itself. Each point represents five simulated trials."),
        section("4. Worked calculations and uncertainty",[
          f"For the 450° command at power 50%, mean external angle = {sample['mean_external_deg']:.2f}°, s = {sample['sd_external_deg']:.3f}°, mean duration = {sample['mean_duration_s']:.3f} s. Raw rows are retained in motor_trials.csv so all means and scatter can be recalculated.",
          "The uncertainty calculation treats the independent reference noise/reporting step as an additional conservative type-B component. Quantization of the tacho is already present in the calibration residuals; it is not added again to the external-reference uncertainty. This simplified budget excludes real mounting error, backlash, drift and load-dependent deformation." ],
          calculations=[
            "x̄ = Σxi/n; s = √[Σ(xi − x̄)²/(n − 1)].",
            f"e = {sample['mean_external_deg']:.2f}° − 450° = {sample['bias_deg']:.2f}°; relative error = 100 e/450 = {sample['relative_error_pct']:.3f}%.",
            f"u_ref = √(0.35² + 0.5²/12) = {math.sqrt(.35**2+.5**2/12):.3f}°; U = 2√(s²/5 + u_ref²) = {sample['expanded_uncertainty_deg']:.2f}°.",
            f"s_wheel = πD θ/360 = π × 56 mm × {sample['mean_external_deg']:.2f}/360 = {math.pi*D_MM*sample['mean_external_deg']/360:.2f} mm.",
            "One degree at D = 56 mm corresponds to π × 56/360 = 0.489 mm of nominal rolling travel. This conversion assumes no slip.",
            "For an in-place body turn ψ = 10°, each wheel travels ±Bψ/2 = ±10.472 mm (ψ in radians); required shaft angle = ±Bψ(deg)/D = ±21.429°. Body heading and shaft angle are different quantities." ]),
        section("5. Counter resets and displayed position",[
          "The official NXC API distinguishes the tachometer count/limit reset from the program-relative rotation count reset. ResetTachoCount acts on the tacho counter and its limit goal. ResetRotationCount acts on the program-relative position counter read with MotorRotationCount. Resetting a counter changes its zero reference; it does not physically return the shaft to zero.",
          "The exact trace below isolates reset semantics with relative movement increments. In a brick program, movement helpers may request their own counter resets; read values before and after the helper and verify which counter is displayed. Apply resets while stopped and allow the firmware update to complete before interpreting the result.",
          "For a readable screen show target angle, current relative tacho angle, unwrapped program-relative angle and trial time with units. To show orientation within one revolution use ((angle % 360) + 360) % 360; retain the unwrapped angle in the file." ],
          ["Event","Physical shaft (°)","Tacho (°)","Program relative (°)"],[[r['event'],r['shaft_deg'],r['tacho_count_deg'],r['program_rotation_deg']] for r in resets]),
        section("6. Conclusion and reproducibility",[
          f"The modeled motor performed both directions and all requested rotations. Across the 60 trials, mean absolute command error of the independent observations was {mean([abs(r['command_error_external_deg']) for r in rows]):.3f}°. This is a simulator result, not a real NXT accuracy claim.",
          "The useful result is a traceable test method: an independent angle check, a calibration equation, repeated observations, signed/relative errors, uncertainty and elapsed time. Counter-reset behavior is explicit, so the screen can show what its zero means. For physical validation mark the shaft, measure the true rotation independently, repeat the same matrix and replace the generated CSVs with logged readings.",
          "Reproduce with simulation/lab_simulations.py. Seed = 20261014. Files: motor_calibration.csv, motor_trials.csv, motor_summary.csv and motor_counter_reset_trace.csv. Self-checks cover trial count, independent readings, gain recovery, negative direction and zero-reference behavior." ])
      ],"references":["Supplied Screenshot_2.png: Report_1 Exploring motors (4h).","Supplied __NXC_tutorial.pdf, pp. 31–34: limited-angle motion, sign convention and PID explanation.",
       "NXC official API, Output module functions: https://bricxcc.sourceforge.net/nbc/nxcdoc/nxcapi/group___output_module_functions.html",
       "NXC official API, ResetTachoCount: https://bricxcc.sourceforge.net/nbc/nxcdoc/nxcapi/group___output_module_functions_ga89b494fec2591253658a55cc74d7c6e7.html",
       "NXC official API, ResetRotationCount: https://bricxcc.sourceforge.net/nbc/nxcdoc/nxcapi/group___output_module_functions_ga1f07b7f5f06116fffe738f699d0ce83f.html"]}
    return report, {"motor_trials":len(rows),"motor_calibration_gain":a,"motor_calibration_offset_deg":b,"motor_mean_absolute_error_deg":mean([abs(r['command_error_external_deg']) for r in rows]),"motor_worst_mean_error_deg":worst['bias_deg']}


def sonar_simulation():
    def read(d):
        if d<8 or d>=250: return 255
        return round(1.006*d+0.30+RNG.gauss(0,.25+.004*d))
    calibration=[]
    for d in (20,40,80):
        for trial in range(1,11):
            calibration.append({"distance_truth_cm":d,"trial":trial,"reference_observed_cm":round(d+RNG.gauss(0,.1),3),"sonar_raw_cm":read(d)})
    a,b,resid,mx,sxx=linear_fit([r['reference_observed_cm'] for r in calibration],[r['sonar_raw_cm'] for r in calibration])
    csv_write("sonar_calibration.csv",calibration)
    rows=[]; summaries=[]
    for d in (5,10,20,40,80,120,180,240):
        group=[]
        for trial in range(1,11):
            y=read(d); valid=y!=255
            r={"distance_truth_cm":d,"trial":trial,"sonar_raw_cm":y,"valid":int(valid),"sonar_calibrated_cm":round((y-b)/a,6) if valid else "", "raw_error_cm":round(y-d,6) if valid else "", "read_call_latency_ms":round(max(.5,RNG.gauss(3.2,.28)),3)}
            rows.append(r); group.append(r)
        vals=[r['sonar_raw_cm'] for r in group if r['valid']]
        corr=[r['sonar_calibrated_cm'] for r in group if r['valid']]
        if vals:
            pred_u=(resid/a)*math.sqrt(1/len(calibration)+(d-mx)**2/sxx)
            u=math.sqrt(sd(corr)**2/len(corr)+.20**2+pred_u**2)
            summaries.append({"truth_cm":d,"valid_n":len(vals),"raw_mean_cm":mean(vals),"raw_sd_cm":sd(vals),"raw_bias_cm":mean(vals)-d,"corrected_mean_cm":mean(corr),"corrected_bias_cm":mean(corr)-d,"expanded_u_cm":2*u})
        else:
            summaries.append({"truth_cm":d,"valid_n":0,"raw_mean_cm":"","raw_sd_cm":"","raw_bias_cm":"","corrected_mean_cm":"","corrected_bias_cm":"","expanded_u_cm":""})
    csv_write("sonar_distance_trials.csv",rows);csv_write("sonar_distance_summary.csv",summaries)
    sweep=[]; sweepsummary=[]
    for distance in (50,100):
        half=12+math.degrees(math.atan(10/distance))
        for angle in range(-40,41,5):
            prob=1/(1+math.exp((abs(angle)-half)/2.5))
            hits=0
            for trial in range(1,11):
                detected=RNG.random()<prob
                hits+=detected
                sweep.append({"target_distance_cm":distance,"target_width_cm":20,"off_axis_deg":angle,"trial":trial,"injected_detection_probability":round(prob,6),"detected":int(detected),"distance_read_cm":read(distance) if detected else 255})
            sweepsummary.append({"target_distance_cm":distance,"off_axis_deg":angle,"detections":hits,"n":10,"detection_pct":hits*10})
    csv_write("sonar_angular_trials.csv",sweep);csv_write("sonar_angular_summary.csv",sweepsummary)
    latency=[]; latest=120; update_time=0
    for t in range(0,601,20):
        fresh=t%80==0
        if fresh:
            update_time=t
            if t>=290:
                latest=round(40+80*math.exp(-(t-290)/25))
            else: latest=120
        latency.append({"time_ms":t,"target_truth_cm":120 if t<250 else 40,"sonar_observed_cm":latest,"fresh_sensor_update":int(fresh),"cached_age_ms":t-update_time,"read_call_ms":round(max(.5,RNG.gauss(3.2,.28)),3)})
    csv_write("sonar_step_response.csv",latency)
    first=next(r['time_ms'] for r in latency if r['time_ms']>=250 and r['sonar_observed_cm']!=120)
    settling=next(r['time_ms'] for r in latency if r['time_ms']>=250 and abs(r['sonar_observed_cm']-40)<=2)
    spans={d:[r['off_axis_deg'] for r in sweepsummary if r['target_distance_cm']==d and r['detections']>=8] for d in (50,100)}
    check("Sonar missing echo excluded from statistics",summaries[0]['valid_n']==0)
    check("Sonar distance trials",len(rows)==80)
    check("Sonar angular experiment count",len(sweep)==340)
    check("Cached reads do not count as fresh updates",sum(r['fresh_sensor_update'] for r in latency)==8)
    check("Read latency differs from physical response",first-250>mean([r['read_call_ms'] for r in latency]))
    fig1=plot_xy("sonar_accuracy.png","Sonar accuracy: bias before and after separate calibration",[
        ("Raw bias",[(r['truth_cm'],r['raw_bias_cm']) for r in summaries if r['valid_n']]),
        ("Calibrated bias",[(r['truth_cm'],r['corrected_bias_cm']) for r in summaries if r['valid_n']])],"Reference distance (cm)","Mean signed error (cm)",ylim=(-2,3))
    fig2=plot_xy("sonar_detection_sweep.png","Sonar angular detection sweep: 20 cm planar target",[(f"Target at {d} cm",[(r['off_axis_deg'],r['detection_pct']) for r in sweepsummary if r['target_distance_cm']==d]) for d in (50,100)],"Off-axis target angle (degrees)","Detection rate (%)",ylim=(0,100))
    fig3=plot_xy("sonar_step_response.png","Sonar step response: fresh updates and cached observations",[("True target distance",[(r['time_ms'],r['target_truth_cm']) for r in latency]),("Observed cached distance",[(r['time_ms'],r['sonar_observed_cm']) for r in latency])],"Time (ms)","Distance (cm)",ylim=(0,140))
    return {"a":a,"b":b,"resid":resid,"rows":rows,"summary":summaries,"sweep":sweepsummary,"spans":spans,"latency":latency,"first_delay_ms":first-250,"settling_ms":settling-250,"fig_accuracy":fig1,"fig_sweep":fig2,"fig_step":fig3}


SWATCH={"red":(.80,.10,.07),"green":(.12,.70,.12),"blue":(.08,.15,.78),"yellow":(.78,.70,.08),"white":(.84,.84,.84),"black":(.035,.035,.035)}
GAIN=(1.0,.91,1.07)
DARK=(22,25,21)


def color_class(norm):
    # Transparent custom classifier. This is not the LEGO firmware classifier.
    r,g,b=norm
    if max(norm)<.085: return "black"
    if min(norm)>.58 and max(norm)-min(norm)<.15: return "white"
    if r>.35 and g>.30 and b<.20: return "yellow"
    total=sum(norm)
    if total<=.04:return "unknown"
    shares=[v/total for v in norm]
    winner=max(range(3),key=lambda i:shares[i])
    return ("red","green","blue")[winner] if shares[winner]>.55 else "unknown"


def color_simulation():
    # Background illumination and standoff explicitly affect the generated signal.
    # Raw RGB+blank counts emulate a four-channel log layout, not ADC specifications.
    rows=[];groups={}
    white=(1,1,1)
    for name,refl in SWATCH.items():
        for lux in (100,300,800):
            for distance in (10,20,30):
                group=[]
                for trial in range(1,6):
                    # Active reflection follows a simple inverse-square falloff.
                    illumination=1/(1+(distance/18)**2)
                    ambient=.18*lux
                    blank=round(ambient+RNG.gauss(0,2.0))
                    raw=[round(DARK[i]+ambient+GAIN[i]*800*illumination*refl[i]+RNG.gauss(0,4.5+.006*lux)) for i in range(3)]
                    # White reference recorded at the same light and distance.
                    white_raw=[round(DARK[i]+ambient+GAIN[i]*800*illumination+RNG.gauss(0,4.5+.006*lux)) for i in range(3)]
                    normalized=[max(0,(raw[i]-DARK[i]-blank)/(white_raw[i]-DARK[i]-blank)) for i in range(3)]
                    observed=color_class(normalized)
                    row={"swatch_truth":name,"ambient_lux_assumed":lux,"standoff_mm":distance,"trial":trial,
                         "raw_R_count":raw[0],"raw_G_count":raw[1],"raw_B_count":raw[2],"raw_blank_count":blank,
                         "white_R_count":white_raw[0],"white_G_count":white_raw[1],"white_B_count":white_raw[2],
                         "norm_R_ratio":round(normalized[0],6),"norm_G_ratio":round(normalized[1],6),"norm_B_ratio":round(normalized[2],6),
                         "custom_class":observed,"correct":int(observed==name),"software_read_ms":round(max(.4,RNG.gauss(2.1,.2)),3)}
                    rows.append(row);group.append(row)
                groups[(name,lux,distance)]=group
    csv_write("color_trials.csv",rows)
    summaries=[]
    for (name,lux,distance),g in groups.items():
        summaries.append({"swatch":name,"ambient_lux_assumed":lux,"standoff_mm":distance,"n":5,
             "raw_R_mean_count":mean([r['raw_R_count'] for r in g]),"raw_R_sd_count":sd([r['raw_R_count'] for r in g]),
             "norm_R_mean_ratio":mean([r['norm_R_ratio'] for r in g]),"norm_R_sd_ratio":sd([r['norm_R_ratio'] for r in g]),
             "norm_G_mean_ratio":mean([r['norm_G_ratio'] for r in g]),"norm_B_mean_ratio":mean([r['norm_B_ratio'] for r in g]),
             "correct_n":sum(r['correct'] for r in g)})
    csv_write("color_summary.csv",summaries)
    confusion=[]
    for actual in SWATCH:
        r={"truth":actual}
        for predicted in list(SWATCH)+["unknown"]:
            r[predicted]=sum(row['swatch_truth']==actual and row['custom_class']==predicted for row in rows)
        confusion.append(r)
    csv_write("color_confusion_matrix.csv",confusion)
    timing=[]
    # Step white to red at 250 ms: response delay=30 ms, tau=20 ms,
    # fresh update every 40 ms, loop samples every 10 ms.
    latest=SWATCH['white'];last_update=0
    for t in range(0,501,10):
        fresh=t%40==0
        if fresh:
            last_update=t
            alpha=0 if t<280 else 1-math.exp(-(t-280)/20)
            latest=tuple((1-alpha)*SWATCH['white'][i]+alpha*SWATCH['red'][i] for i in range(3))
        timing.append({"time_ms":t,"truth_class":"white" if t<250 else "red","normalized_R_ratio":round(latest[0],6),"normalized_G_ratio":round(latest[1],6),"normalized_B_ratio":round(latest[2],6),"observed_class":color_class(latest),"fresh_update":int(fresh),"cached_age_ms":t-last_update})
    csv_write("color_step_response.csv",timing)
    redtime=next(r['time_ms'] for r in timing if r['time_ms']>=250 and r['observed_class']=='red')
    # 10%-90% transition based on channels, not time to classify once.
    first10=next(r['time_ms'] for r in timing if r['time_ms']>=250 and (SWATCH['white'][1]-r['normalized_G_ratio'])/(SWATCH['white'][1]-SWATCH['red'][1])>=.1)
    first90=next(r['time_ms'] for r in timing if r['time_ms']>=250 and (SWATCH['white'][1]-r['normalized_G_ratio'])/(SWATCH['white'][1]-SWATCH['red'][1])>=.9)
    # Modes with red illumination measure intensity; no-light mode ambient only.
    modes=[]
    for name,refl in SWATCH.items():
        g=groups[(name,300,20)]
        for r in g:
            modes.append({"swatch":name,"trial":r['trial'],"ambient_lux_assumed":300,"standoff_mm":20,
                          "color_full_custom_class":r['custom_class'],"red_active_raw_count":r['raw_R_count'],"none_ambient_raw_count":r['raw_blank_count'],
                          "red_reflectance_scaled_pct":round(r['norm_R_ratio']*100,3)})
    csv_write("color_mode_comparison.csv",modes)
    check("Color factorial coverage",len(rows)==270)
    check("RGB/blank channel logging",all(all(k in r for k in ('raw_R_count','raw_G_count','raw_B_count','raw_blank_count')) for r in rows))
    check("Color confusion matrix total",sum(sum(v for k,v in r.items() if k!='truth') for r in confusion)==270)
    check("Color output responds after physical step",redtime>250)
    check("Color normalization uses same-condition white reference",all(r['white_R_count']>r['raw_blank_count']+DARK[0] for r in rows))
    # Local radiometric resolution relative to trial scatter, no ADC bit-depth claim.
    baseline=groups[('red',300,20)]
    sigmar=sd([r['raw_R_count'] for r in baseline]); normsd=sd([r['norm_R_ratio'] for r in baseline])
    fig=plot_xy("color_light_distance.png","Red swatch: raw signal depends on light and mounting distance",[(f"Ambient {lux} lux",[(distance,mean([r['raw_R_count'] for r in groups[('red',lux,distance)]])) for distance in (10,20,30)]) for lux in (100,300,800)],"Sensor standoff (mm)","Raw red channel (model counts)",ylim=(0,750))
    fig2=plot_xy("color_response.png","Color physical response: white-to-red transition",[(label,[(r['time_ms'],r[key]) for r in timing]) for label,key in [('Red channel','normalized_R_ratio'),('Green channel','normalized_G_ratio'),('Blue channel','normalized_B_ratio')]],"Time (ms)","Normalized reflectance ratio",ylim=(0,1))
    return {"rows":rows,"summary":summaries,"groups":groups,"confusion":confusion,"timing":timing,"red_delay_ms":redtime-250,"rise_10_90_ms":first90-first10,"accuracy_pct":100*sum(r['correct'] for r in rows)/len(rows),"raw_R_sigma":sigmar,"norm_R_sigma":normsd,"figure":fig,"figure_timing":fig2}


def gyro_simulation():
    # Educational single-axis rate gyro model: not an installed sensor claim.
    cal=[RNG.gauss(.8,.18) for _ in range(100)]
    bias=mean(cal)
    calrows=[{"sample":i+1,"truth_rate_deg_s":0,"raw_rate_deg_s":round(v,6)} for i,v in enumerate(cal)]
    csv_write("gyro_stationary_calibration.csv",calrows)
    rows=[]; heading=0;rawheading=0;truthheading=0
    for i in range(500):
        time_s=(i+1)*.01
        true=45 if .5<time_s<=2.5 else 0
        measured=true+.8+RNG.gauss(0,.18)
        heading+=(measured-bias)*.01
        rawheading+=measured*.01
        truthheading+=true*.01
        rows.append({"time_s":round(time_s,3),"truth_rate_deg_s":true,"observed_rate_deg_s":round(measured,6),"bias_corrected_rate_deg_s":round(measured-bias,6),"truth_heading_deg":round(truthheading,6),"integrated_raw_heading_deg":round(rawheading,6),"integrated_corrected_heading_deg":round(heading,6)})
    csv_write("gyro_turn_trace.csv",rows)
    check("Gyro integrated truth equals ninety degree turn",abs(truthheading-90)<1e-6)
    check("Stationary bias calibration improves turn integral",abs(heading-truthheading)<abs(rawheading-truthheading))
    return {"bias":bias,"truth":truthheading,"corrected":heading,"raw":rawheading,"stationary_sd":sd(cal)}


def sensor_report(sonar,color,gyro):
    sonartable=[]
    for s in sonar['summary']:
        if not s['valid_n']:
            sonartable.append([str(s['truth_cm'])+" (0/10)","No echo","—","—","—","—"])
        else:
            sonartable.append([str(s['truth_cm'])+f" ({s['valid_n']}/10)",fmt(s['raw_mean_cm']),fmt(s['raw_sd_cm']),fmt(s['raw_bias_cm']),fmt(s['corrected_bias_cm']),fmt(s['expanded_u_cm'])])
    colorbase=[s for s in color['summary'] if s['ambient_lux_assumed']==300 and s['standoff_mm']==20]
    color_table=[[s['swatch'],fmt(s['raw_R_mean_count'],1)+" ± "+fmt(s['raw_R_sd_count']),fmt(s['norm_R_mean_ratio'],3),fmt(s['norm_G_mean_ratio'],3),fmt(s['norm_B_mean_ratio'],3),f"{s['correct_n']}/5"] for s in colorbase]
    bycondition=[]
    for lux in (100,300,800):
        for d in (10,20,30):
            group=[r for r in color['rows'] if r['ambient_lux_assumed']==lux and r['standoff_mm']==d]
            bycondition.append([str(lux),str(d),str(sum(r['correct'] for r in group))+"/30",fmt(100*sum(r['correct'] for r in group)/30,1)])
    baseline=next(s for s in colorbase if s['swatch']=='red')
    nominal=max(s['raw_bias_cm'] for s in sonar['summary'] if s['valid_n'])
    corrected_mae=mean([abs(r['sonar_calibrated_cm']-r['distance_truth_cm']) for r in sonar['rows'] if r['valid']])
    return {"id":"report_2","title":"Report 2 — Exploring sonar and color sensors","source":"Screenshot_3.png; __NXC_tutorial.pdf, p. 21",
      "summary":f"Omar Zid | Reproducible simulation | 80 sonar distance trials, 340 angular trials and 270 color trials. Color classification: {color['accuracy_pct']:.1f}% in the declared model. Software read time, fresh sampling and physical response are reported separately.",
      "sections":[
       section("1. Aim, apparatus model and procedure",[
        "The task asks for sonar speed, accuracy and field of action; color speed, resolution, response to color and illumination; and the operating principle and uses of one further sensor. This report selects a single-axis rate gyroscope for the final part.",
        "A simulated stationary rig positions a broad target at 5–240 cm, then sweeps a 20 cm target through −40° to +40° at two distances. A color rig varies six matte swatches, assumed ambient illumination 100/300/800 lux and sensor standoff 10/20/30 mm. Ten sonar and five color repetitions per condition retain raw readings. The target geometry, timing constants, signal steps and noise values below are assumptions, not verified LEGO specifications.",
        "Distance references have an assumed standard uncertainty 0.20 cm. Lux values are controlled simulator inputs, not measured light-meter readings. Separate calibration data are generated before test trials. A fixed random seed makes every observation reproducible and identifiable as simulated." ]),
       section("2. Sonar calibration, accuracy and uncertainty",[
        "The valid-range model returns round(1.006d + 0.30 cm + Gaussian noise), with noise σ = 0.25 cm + 0.004d. It deliberately returns a no-echo sentinel at d < 8 cm or d ≥ 250 cm. These boundaries and the 1 cm output step are illustrative model settings. No-echo values are not averaged as if they were target distances.",
        f"Thirty calibration observations at 20, 40 and 80 cm yielded y = {sonar['a']:.6f}d + {sonar['b']:.5f} cm; residual standard deviation {sonar['resid']:.3f} cm. Correct distances using dcal = (y − b)/a. The independent test matrix shows maximum raw mean bias {nominal:.2f} cm; mean absolute calibrated individual error is {corrected_mae:.3f} cm.",
        "Sample s describes repeatability of the raw distance observations. Corrected bias compares the calibrated mean with the known model distance. Expanded uncertainty U uses k = 2 and includes mean repeatability, assumed reference uncertainty and linear-calibration prediction uncertainty. Long-distance values extrapolate beyond the 80 cm calibration range; their larger uncertainty and sensitivity to slope are retained." ],
        ["Truth cm (n)","Raw mean (cm)","s (cm)","Raw bias (cm)","Cal. bias (cm)","U cal. (cm)"],sonartable,
        calculations=["e = x̄ − dref; MAE = Σ|xi − dref|/n; s = √[Σ(xi − x̄)²/(n − 1)].",
          "u_cal(d) = (s_fit/a)√[1/Ncal + (d − d̄cal)²/Σ(dj − d̄cal)²].",
          "U = 2√[s_corrected²/n + (0.20 cm)² + u_cal(d)²]. Output quantization is present in trial scatter and calibration residuals, so it is not added twice.",
          "A 1 cm reporting step does not imply ±1 cm accuracy. Systematic bias, reflectivity, target angle, multiple echoes and temperature can affect a physical sensor." ],
        figure=sonar['fig_accuracy'],caption="Separate calibration reduces the injected scale/offset error. It does not guarantee real-world accuracy."),
       section("3. Angular field of action",[
        "Detection is generated using P = 1/[1 + exp((|α| − h)/2.5°)], where h = 12° + atan(10 cm/d) in degrees. The assumed 12° core and 2.5° transition width are model constants. Target width contributes to the apparent field, so a measured detection cone is specific to this target and range.",
        f"At least 8 detections out of 10 defined the operational threshold. For the 20 cm target at 50 cm, accepted sampled angles ran from {min(sonar['spans'][50])}° to {max(sonar['spans'][50])}°; at 100 cm they ran from {min(sonar['spans'][100])}° to {max(sonar['spans'][100])}°. The sweep spacing is 5°; threshold boundaries are therefore only localized to approximately one angular sample, and finite trials add binomial uncertainty.",
        "A physical field-of-view test must use a fixed object and a repeatable turntable, record misses and repeated hits, and state target material, dimensions, distance and criterion. A single sonar reading cannot prove that the entire surrounding region is clear." ],
        figure=sonar['fig_sweep'],caption="Detection percentage versus off-axis angle for two distances. These curves are generated by the declared model and do not assert a manufacturer's beam specification."),
       section("4. Speed: software read, update interval and physical response",[
        f"Mean simulated sonar read-call latency is {mean([r['read_call_latency_ms'] for r in sonar['rows']]):.2f} ms. A software loop reads every 20 ms, while the assumed sonar state refreshes every 80 ms. Faster polling repeats cached data. A target step from 120 to 40 cm occurs at 250 ms; response delay is 40 ms and time constant 25 ms. The first changed observation appears after {sonar['first_delay_ms']} ms, and the reading reaches ±2 cm of its final value after {sonar['settling_ms']} ms.",
        "These three times answer different questions: how long a function call blocks; how often fresh measurements become available; and how quickly a changed physical target affects the reported output. Only the latter two constrain a stopping controller. Reading faster is useful for scheduling but does not manufacture fresh sensor information.",
        f"For the color step test, software reads average {mean([r['software_read_ms'] for r in color['rows']]):.2f} ms; assumed fresh updates occur every 40 ms. The physical model has 30 ms delay and 20 ms time constant. A white-to-red step at 250 ms is first classified red after {color['red_delay_ms']} ms. The sampled 10–90% green-channel transition spans {color['rise_10_90_ms']} ms; 40 ms sampling limits its time resolution." ],
        figure=sonar['fig_step'],caption="A 20 ms polling loop repeatedly sees the same value between fresh 80 ms updates. The physical response time is much longer than the read-call latency."),
       section("5. Color channels, calibration and lighting response",[
        "Full-color logs contain simulated raw red/green/blue and a blank ambient channel. Per-channel dark offsets are (22, 25, 21) counts and gains (1.00, 0.91, 1.07). Raw counts follow dark + 0.18 × lux + gain × 800 × ρ/[1 + (h/18 mm)²] + noise. Channel noise σ = 4.5 + 0.006 × lux counts. A white reference under the same light and standoff normalizes each channel.",
        "The ratio norm = (raw − dark − blank)/(white − dark − blank) estimates reflectance in the model. Raw RGB responds to mounting distance and ambient light; subtracting the blank and dividing by a matched white reduces these changes. Normalized ratios are custom calculated values. They are not claimed to be the firmware's normalized arrays or its built-in classifier.",
        "NXC exposes full-color, red/green/blue illumination and no-light configurations. ReadSensorColorEx returns a color value plus raw, normalized and scaled arrays; the raw/array API requires compatible NXT 2.0 firmware. The custom CSV separately records our reproducible classifier. Red-only illumination yields an intensity measurement; no-light mode supports ambient measurement and comparison." ],
        ["Swatch","Raw R mean ± s","Norm R","Norm G","Norm B","Correct n"],color_table,
        calculations=["ρR = (Rraw − Rdark − blank)/(Rwhite − Rdark − blank); equivalent expressions for G and B.",
          f"Red at 300 lux and 20 mm: normalized R mean = {baseline['norm_R_mean_ratio']:.3f}, sample s = {baseline['norm_R_sd_ratio']:.4f}. Mean standard error = s/√5 = {baseline['norm_R_sd_ratio']/math.sqrt(5):.4f}.",
          f"The assumed raw output step is one model count; trial σR = {color['raw_R_sigma']:.2f} counts. A 3s discrimination criterion is approximately {3*color['raw_R_sigma']:.1f} counts or {3*color['norm_R_sigma']:.3f} in normalized R under this condition. This is practical modeled resolution, not sensor ADC bit depth." ],
        figure=color['figure'],caption="Each point averages five red-swatch trials. Ambient light raises raw readings and larger standoff reduces active reflection."),
       section("6. Classification and resolution limits",[
        "The classifier first separates black (all normalized channels < 0.085), white (minimum > 0.58 with channel spread < 0.15) and yellow (R > 0.35, G > 0.30, B < 0.20). Otherwise the strongest RGB channel must represent > 55% of total signal; ambiguous outputs are marked unknown. These thresholds are declared design choices, not calibrated real LEGO color IDs.",
        f"The 270 trials achieved {color['accuracy_pct']:.2f}% correct classifications in the declared model. All individual errors remain in color_trials.csv and the full confusion matrix. A high classification score for these separated swatches does not establish the number of colors a real sensor can distinguish or its smallest intensity increment.",
        "Resolution is evaluated from within-condition scatter and the reporting step. Color identification, reflectance resolution and light intensity are separate outputs. Larger standoff weakens the reflected signal; larger ambient illumination raises noise in this model. For a real test, include near-threshold shades, glossy surfaces and shadow changes, and replace assumed lux with a light-meter observation." ],
        ["Ambient (lux)","Standoff (mm)","Correct / trials","Accuracy (%)"],bycondition,
        figure=color['figure_timing'],caption="Normalized channels converge after the modeled physical white-to-red step; successful classification is a threshold event during that transition."),
       section("7. Further sensor: single-axis rate gyroscope",[
        "A rate gyroscope measures angular velocity about its sensitive axis. With a known starting orientation, numerical integration estimates the change of heading. It does not directly provide an absolute compass heading. The official FIRST implementation documentation for the legacy HiTechnic NXT gyro describes a single-axis rate output; this report uses its operating principle without assuming that such a sensor is physically present.",
        f"In a separate illustrative model, stationary rate bias is +0.8°/s with noise σ = 0.18°/s. Average 100 stationary samples before motion: estimated bias {gyro['bias']:.4f}°/s, s = {gyro['stationary_sd']:.4f}°/s. Sample at an assumed 100 Hz. A true 45°/s turn lasting 2 s gives 90°. Over the complete 5 s trace, uncorrected integration gives {gyro['raw']:.3f}°; bias-corrected integration gives {gyro['corrected']:.3f}°.",
        "Applications include turn-angle feedback, detecting unintended rotation, balancing control and comparing wheel odometry with body rotation. Remaining bias causes heading drift proportional to elapsed time; vibration, temperature changes and axis alignment require calibration. Combine rate with wheel encoders or a compass for longer-term orientation. Compass readings can be disturbed by local magnetic fields; an accelerometer measures specific force and cannot separate tilt from all vehicle accelerations without further assumptions." ],
        calculations=["b̂ = (1/N)Σωstationary; ωcorrected = ωraw − b̂.",
          "θk = θk−1 + ωcorrected,k Δt; units: (degrees/second) × seconds = degrees.",
          "Residual bias 0.1°/s accumulates 6° heading error in 60 s. This is a dimensional example, not a measured drift specification." ]),
       section("8. Conclusions and files",[
        "The models demonstrate a working test approach with separate truth, observation, calibration and error calculations. Sonar misses are explicit; angular detection is target dependent; fresh updates and physical response govern usable speed. Color calibration improves consistency, while raw intensity alone depends on illumination and geometry. The rate gyro example shows why stationary bias subtraction is essential before integration.",
        "Reproduce with simulation/lab_simulations.py, seed 20261014. Sonar files: calibration, distance trials/summary, angular trials/summary and step response. Color files: trials/summary, confusion matrix, mode comparison and step response. Gyro files: stationary calibration and turn trace. All are CSVs under data/labs. No physical measurements, manufacturer precision or installed-device claims are implied." ])
      ],"references":["Supplied Screenshot_3.png: Report_2 Exploring sonar and color sensor (4h).","Supplied __NXC_tutorial.pdf, p. 21: ultrasonic sensor example and low-speed configuration.",
        "NXC official API, Input module functions: https://bricxcc.sourceforge.net/nbc/nxcdoc/nxcapi/group___input_module_functions.html",
        "NXC official API, Color sensor array indices: https://bricxcc.sourceforge.net/nbc/nxcdoc/nxcapi/group___input_color_idx_constants.html",
        "FIRST official legacy HiTechnic gyro implementation documentation: https://first-tech-challenge.github.io/SkyStone/com/qualcomm/hardware/hitechnic/HiTechnicNxtGyroSensor.html"]}


def ray_clearance(angle):
    """Exact ray cast in a rectangular model room containing two round obstacles."""
    ux,uy=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    hits=[]
    for x in (-1000,2000):
        if abs(ux)>1e-9:
            t=x/ux
            if t>0 and -1200<=t*uy<=1500: hits.append(t)
    for y in (-1200,1500):
        if abs(uy)>1e-9:
            t=y/uy
            if t>0 and -1000<=t*ux<=2000: hits.append(t)
    for cx,cy,radius in ((900,0,200),(-500,-500,180)):
        projection=cx*ux+cy*uy
        perpendicular2=cx*cx+cy*cy-projection*projection
        if perpendicular2<=radius*radius and projection>0:
            t=projection-math.sqrt(radius*radius-perpendicular2)
            if t>0:hits.append(t)
    return min(hits)


def polar_figure(scan,best):
    im=Image.new("RGB",(1250,1080),"white");draw=ImageDraw.Draw(im)
    cx,cy=625,590;scale=.155
    draw.text((75,35),"Environment scanner: 360° simulated polar map",font=font(32),fill="#14213d")
    draw.text((75,85),"Omar Zid  |  10° headings  |  three sonar reads per heading  |  seed 20261014",font=font(22),fill="#667085")
    for r in (500,1000,1500,2000,2500):
        rp=r*scale
        draw.ellipse((cx-rp,cy-rp,cx+rp,cy+rp),outline="#d0d5dd",width=2)
        draw.text((cx+12,cy-rp+4),f"{r} mm",font=font(18),fill="#667085")
    for a in range(0,360,30):
        rad=math.radians(a);xp=cx+math.cos(rad)*410;yp=cy-math.sin(rad)*410
        draw.line((cx,cy,xp,yp),fill="#e7ebf0",width=2)
        draw.text((xp-18,yp-12),f"{a}°",font=font(20),fill="#344054")
    def pt(a,d):
        return (cx+math.cos(math.radians(a))*d*scale,cy-math.sin(math.radians(a))*d*scale)
    truth=[pt(r['heading_deg'],r['clearance_truth_mm']) for r in scan]
    obs=[pt(r['heading_deg'],r['mean_observed_cm']*10) for r in scan]
    draw.line(truth+[truth[0]],fill="#94a3b8",width=3)
    draw.line(obs+[obs[0]],fill="#2563eb",width=5)
    for p in obs:draw.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill="#2563eb")
    endpoint=pt(best,2000)
    draw.line((cx,cy,*endpoint),fill="#059669",width=7)
    redpt=pt(best,650)
    draw.ellipse((redpt[0]-12,redpt[1]-12,redpt[0]+12,redpt[1]+12),fill="#dc2626")
    draw.text((75,1040),f"Best conservative heading: {best}°  |  red-strip onset: 650 mm",font=font(25),fill="#14213d")
    path=FIG/"intro_scan_polar.png";im.save(path);return path


def intro_simulation():
    raw=[];scan=[]
    for angle in range(0,360,10):
        truth=ray_clearance(angle)
        reads=[]
        for trial in range(1,4):
            observed=round(truth/10+.3+.006*truth/10+RNG.gauss(0,.25+.004*truth/10))
            reads.append(observed)
            raw.append({"heading_deg":angle,"trial":trial,"clearance_truth_mm":round(truth,6),"sonar_observed_cm":observed})
        scan.append({"heading_deg":angle,"clearance_truth_mm":round(truth,6),"mean_observed_cm":mean(reads),"sample_sd_cm":sd(reads)})
    for i,r in enumerate(scan):
        r['conservative_score_cm']=min(scan[(i-1)%36]['mean_observed_cm'],r['mean_observed_cm'],scan[(i+1)%36]['mean_observed_cm'])
    best=max(scan,key=lambda r:r['conservative_score_cm'])
    csv_write("intro_scan_trials.csv",raw);csv_write("intro_scan_summary.csv",scan)
    # Body orientation after scan returns to zero; the chosen direction is relative
    # to this frame. A real implementation should verify the complete scan angle.
    target_heading=best['heading_deg']
    v=120.0;pos=0.0;redcount=0;state="moving";trace=[];stopcommand=None
    dt=.01
    lastclass="white"
    for k in range(850):
        t=k*dt
        if k%5==0:
            delayed_pos=max(0,pos-.040*v)
            lastclass="red" if 650<=delayed_pos<=740 else "white"
            redcount=redcount+1 if lastclass=='red' else 0
            if state=='moving' and redcount>=2:
                state='braking';stopcommand=t
        trace.append({"time_s":round(t,3),"travel_truth_mm":round(pos,6),"speed_truth_mm_s":round(v,6),
                      "surface_truth":"red" if 650<=pos<=740 else "white","observed_color":lastclass,
                      "consecutive_red_reads":redcount,"state":state,"heading_deg":target_heading,
                      "remaining_obstacle_truth_cm":round((ray_clearance(target_heading)-pos)/10,6)})
        if state=='stopped':break
        if state=='braking':
            vnext=max(0,v-600*dt)
            pos+=(v+vnext)*dt/2
            v=vnext
            if v==0:state='stopped'
        else:pos+=v*dt
    csv_write("intro_red_stop_trace.csv",trace)
    check("Scanner covers unique full-circle headings",len(scan)==36 and len(set(r['heading_deg'] for r in scan))==36)
    check("Scanner stores three observations per heading",len(raw)==108)
    check("Best direction uses neighbor minimum",best['conservative_score_cm']==max(r['conservative_score_cm'] for r in scan))
    check("Red stop finishes inside modeled red strip",650<=pos<=740,f"terminal={pos:.3f} mm")
    check("Terminal speed is zero",v==0)
    check("Stop event has two confirmed red observations",next(r for r in trace if r['state']=='braking')['consecutive_red_reads']==2)
    check("Scanner avoids obstacle contact",all(r['remaining_obstacle_truth_cm']>30 for r in trace))
    figure=polar_figure(scan,target_heading)
    fig2=plot_xy("intro_stop_trace.png","Red-stop controller: travel and braking trace",[("Travel (mm)",[(r['time_s'],r['travel_truth_mm']) for r in trace]),("Red onset (650 mm)",[(0,650),(trace[-1]['time_s'],650)])],"Elapsed drive time (s)","Distance along selected heading (mm)",ylim=(0,800))
    report={"id":"introduction","title":"Introduction — Environment scanner demonstration","source":"Screenshot_1.png: Introduction (2h — none reports)",
      "summary":f"Omar Zid | Working numerical demonstration. Scanned 36 headings; selected {target_heading}°; stopped on the simulated red strip at {pos:.1f} mm. This optional evidence note supports the introduction's final task; the supplied page says no formal report.",
      "sections":[
       section("1. Task and demonstrable outcome",[
        "The introduction requests a 360° environment scanner that logs observations, visualizes them on the screen, chooses the most free direction, drives that way and stops on red. The supplied page labels this session ‘none reports’. This short evidence note accompanies the code and data so the teacher can inspect the complete calculation and outcome.",
        "The demonstration models a differential-drive robot using NXC-style motor/sensor control concepts. The scan, chosen direction and stopping trace are numerically executed. All environment distances, sensor observations and timing are simulated. A BricxCC installation, brick connection, download, physical screen and device memory operation are not claimed as completed hardware tasks." ]),
       section("2. Geometry, environment and scan method",[
        "Wheel diameter is assumed D = 56 mm; wheel-centre track is assumed B = 120 mm. The model room spans x = −1000 to 2000 mm and y = −1200 to 1500 mm. Two circular obstacles are centred at (900, 0) mm with radius 200 mm and (−500, −500) mm with radius 180 mm. The initial robot centre is (0, 0); heading zero points along +x and positive angles are counterclockwise.",
        "An exact geometric ray cast provides simulator truth. Every 10° heading has three sonar observations, generated with the same scale/offset/noise form as Report 2. The three-reading mean is stored with its sample standard deviation. A whole-body in-place rotation is used conceptually, not a sensor turret; scanning therefore requires opposite wheel movements and a settled read after each turn.",
        "The score at each heading is the minimum mean clearance of that heading and its adjacent ±10° headings. This avoids choosing a narrow isolated maximum. A three-sample smoothing rule does not prove that a real robot fits through a gap; body width, sensor offset, obstacle shape and angular uncertainty still require margin and checks." ],
        calculations=["Body heading step ψ = 10° = 0.174533 rad. Wheel travel magnitude = Bψ/2 = 120 × 0.174533/2 = 10.472 mm.",
         "Wheel shaft step magnitude = 360 × 10.472/(π × 56) = 21.429°. Rotate opposite wheels by ±21.429° for one ideal 10° body turn.",
         "A 360° body scan requires 36 steps and ±771.429° wheel-shaft rotation in this geometry. Shaft angle is not body heading.",
         "Score(θi) = min[mean d(θi−10°), mean d(θi), mean d(θi+10°)] with circular indexing." ],
        figure=figure,caption="The grey outline is ray-cast truth; blue points are observed three-read means. The green line marks the selected heading and the red point marks the strip's onset."),
       section("3. Scan selection and logged evidence",[
        f"The selected direction is {target_heading}°. Its mean observed clearance is {best['mean_observed_cm']:.2f} cm and its conservative neighboring score is {best['conservative_score_cm']:.2f} cm. Geometric truth along that ray is {best['clearance_truth_mm']:.1f} mm. The observed and true values differ because the declared sensor model includes scale, offset, noise and integer-centimeter reporting.",
        "Store heading in degrees and range in centimeters in an on-brick file, with consistent column labels. The desktop simulation saves every raw trial in intro_scan_trials.csv and all means/scores in intro_scan_summary.csv. A simple brick display can show current heading/range, selected heading and motion state; the polar figure here is the detailed teacher-facing visualization.",
        "When a real sonar returns a missing or invalid echo, label it unknown and do not treat it as guaranteed clear space. This scenario remains within the declared model's useful range. A real scanner also needs obstacle monitoring during the drive, a maximum travel limit, a manual stop and safe handling of failed sensor reads." ],
        ["Quantity","Simulated result"],[["Headings / observations","36 / 108"],["Angle spacing","10°"],["Selected heading",f"{target_heading}°"],["Mean range at chosen heading",f"{best['mean_observed_cm']:.2f} cm"],["Conservative score",f"{best['conservative_score_cm']:.2f} cm"],["True ray clearance",f"{best['clearance_truth_mm']:.1f} mm"]]),
       section("4. Red detection, delay and stopping distance",[
        "The robot drives at an assumed 120 mm/s. A red strip spans 650–740 mm along the chosen ray. Color is checked every 50 ms with an assumed 40 ms physical color delay. Two consecutive red observations command braking; deceleration is 600 mm/s². Speed and stopping-distance values are chosen for this simulation and are not motor power-to-speed specifications.",
        f"The brake command occurred at t = {stopcommand:.2f} s; the robot reached zero velocity at t = {trace[-1]['time_s']:.2f} s and x = {pos:.1f} mm. The terminal point lies within the red strip. Remaining ray clearance was {(ray_clearance(target_heading)-pos)/10:.1f} cm. The red stop has a finite overrun and cannot be modeled as an instantaneous halt at 650 mm.",
        "The complete event trace records physical surface, observed color, confirmation count, control state, velocity, traveled distance and remaining clearance. It distinguishes red detection from the final mechanical stop. The report's terminal distance refers to the robot centre; a physical sensor mounted ahead of the axle introduces an additional geometric offset." ],
        calculations=["Nominal braking time = v/a = 120/600 = 0.200 s.",
         "Braking distance = v²/(2a) = 120²/(2 × 600) = 12.0 mm.",
         "Additional sensing/confirmation travel depends on phase: one 40 ms response delay contributes 4.8 mm; one 50 ms confirmation interval contributes 6.0 mm; polling phase can add up to 6.0 mm.",
         f"Terminal overrun beyond strip onset = {pos:.1f} − 650 = {pos-650:.1f} mm; observed finite-phase trace determines this value." ],
        figure=fig2,caption="Travel rises at the modeled drive speed and flattens during braking. The controller stops inside the red strip."),
       section("5. Concurrent tasks, I/O and file handling",[
        "A sensor/logging task can read sensors and update shared state while a movement task issues drive commands. Guard a shared snapshot with a mutex: acquire the lock, copy or update the small state structure, release the lock, then perform slow display/file operations outside the critical section. A mutex prevents inconsistent concurrent access; it does not make sensor data newer.",
        "Buttons should provide start/stop or trial selection; the display should expose state and units. BricxCC offers brick tests, file management and a remote NXT Screen with polling, which supports inspecting a robot with a damaged or inaccessible screen. Files should be opened with a checked status, sized to hold the intended log, closed after writing and downloaded for analysis.",
        "In a simulation, desktop CSV writing demonstrates logging successfully. The NXT file-system capacity, free space and BricxCC transfer remain hardware validation steps. The supplied short guide contains older timing notation; use the full tutorial/API millisecond convention consistently when implementing Wait and timers." ]),
       section("6. Reproducibility and conclusion",[
        f"All scan, score and stop-state checks passed. Seed 20261014 reproduces the same {target_heading}° selection and {pos:.1f} mm terminal travel. The demonstration satisfies the introduction's functional sequence in the model and provides the teacher with visible calculations, plots and raw event data.",
        "Run simulation/lab_simulations.py. Evidence files: intro_scan_trials.csv, intro_scan_summary.csv and intro_red_stop_trace.csv; plots: intro_scan_polar.png and intro_stop_trace.png. Hardware reproduction should replace room assumptions, wheel geometry, sensor offset and timing values with measured inputs while retaining the same logging and analysis method." ])
      ],"references":["Supplied Screenshot_1.png: Introduction (2h — none reports), final Environment Scanner task.","Supplied __NXC_tutorial.pdf: sensors, tasks, mutexes and file operations.","Supplied _NXC_min.pdf: BricxCC basics; compare timing notation with the full tutorial before use."]}
    return report,{"intro_best_heading_deg":target_heading,"intro_best_score_cm":best['conservative_score_cm'],"intro_final_distance_mm":pos,"intro_stop_time_s":trace[-1]['time_s'],"intro_scan_samples":len(raw)}


def main():
    DATA.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True);CONTENT.parent.mkdir(parents=True,exist_ok=True)
    motor,motor_results=motor_simulation()
    sonar=sonar_simulation();color=color_simulation();gyro=gyro_simulation()
    sensors=sensor_report(sonar,color,gyro)
    intro,intro_results=intro_simulation()
    reports=[intro,motor,sensors]
    for report in reports:
        for sec in report['sections']:
            if 'figure' in sec:
                path=Path(sec['figure']);check(f"Figure exists: {path.name}",path.exists() and path.stat().st_size>5000)
    result={**intro_results,**motor_results,"sonar_distance_trials":len(sonar['rows']),"sonar_angular_trials":340,
       "sonar_first_change_delay_ms":sonar['first_delay_ms'],"sonar_settling_delay_ms":sonar['settling_ms'],
       "color_trials":len(color['rows']),"color_accuracy_pct":color['accuracy_pct'],"color_classification_delay_ms":color['red_delay_ms'],
       "gyro_corrected_heading_deg":gyro['corrected'],"gyro_truth_heading_deg":gyro['truth']}
    payload={"student":"Omar Zid","status":"SIMULATION — no physical measurement claim","seed":SEED,"reports":reports,"results":result,"checks":CHECKS,
     "assumptions":{"wheel_diameter_mm":D_MM,"track_mm":TRACK_MM,"all_sensor_noise_and_response_constants":"Educational assumptions, not manufacturer specifications"}}
    CONTENT.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
    (DATA/"lab_results.json").write_text(json.dumps({"seed":SEED,"status":payload['status'],"results":result,"checks":CHECKS},indent=2),encoding='utf-8')
    csv_write("lab_selfchecks.csv",CHECKS)
    print(json.dumps({"content_file":str(CONTENT),"data_directory":str(DATA),"results":result,"checks_passed":sum(c['passed'] for c in CHECKS),"checks_total":len(CHECKS)},indent=2))


if __name__=="__main__":
    main()
