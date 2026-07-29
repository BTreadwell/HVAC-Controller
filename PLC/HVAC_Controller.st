
VAR
    heat_output : BOOL AT %QX0.0;
    cool_output : BOOL AT %QX0.1;
    fan_output : BOOL AT %QX0.2;
    alarm_output : BOOL AT %QX0.3;
    temp_sensor_counts : INT AT %IW0;
    current_state : E_HVAC_STATE;
    fan_shutoff_timer : TON;
    need_fan : BOOL;
    temp_f : REAL;
    min_acceptable_temp : REAL := 40;
    max_acceptable_temp : REAL := 90;
    set_point : REAL := 70.0;
    deadband : REAL := 2.0;
END_VAR

// convert analog temp to fahrenheit. Assume 4mA - 20 mA analog sensor
temp_f := (INT_TO_REAL(temp_sensor_counts) - 5530.0) * 100.0 / (27648.0 - 5530.0);

// determine system state using temp_f and hysteresis
IF temp_f < min_acceptable_temp OR temp_f > max_acceptable_temp THEN
    current_state := E_HVAC_STATE.FAULT;
ELSIF temp_f < (set_point - deadband) OR (temp_f < set_point AND current_state = E_HVAC_STATE.HEAT) THEN
    current_state := E_HVAC_STATE.HEAT;
ELSIF temp_f > (set_point + deadband) OR (temp_f > set_point AND current_state = E_HVAC_STATE.COOL) THEN
    current_state := E_HVAC_STATE.COOL;
ELSE
    current_state := E_HVAC_STATE.OFF;
END_IF;

// update outputs based on current_state

heat_output := FALSE;
cool_output := FALSE;
fan_output := FALSE;
alarm_output := FALSE;
CASE current_state OF
    E_HVAC_STATE.HEAT:
        heat_output := TRUE;
    E_HVAC_STATE.COOL:
        cool_output := TRUE;
    E_HVAC_STATE.OFF:
    E_HVAC_STATE.FAULT:
        alarm_output := TRUE;
        RETURN;
END_CASE;

// additional safety measure to ensure heating/cooling do not run simultaneously
IF heat_output THEN
    cool_output := FALSE;
END_IF;
IF cool_output THEN
    heat_output := FALSE;
END_IF;

// check for fan
need_fan := (current_state = E_HVAC_STATE.HEAT) OR (current_state = E_HVAC_STATE.COOL);
fan_shutoff_timer(IN := NOT need_fan, PT := T#30s);

// turn fan off after 30s delay if not needed
IF need_fan THEN
    fan_output := TRUE;
ELSIF fan_shutoff_timer.Q THEN
    fan_output := FALSE;
ELSE
    fan_output := TRUE;
END_IF;
