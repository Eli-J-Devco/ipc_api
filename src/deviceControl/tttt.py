# Khởi tạo biến toàn cục
integral = 0
previous_error = 0

def pid_controller(setpoint, feedback, Kp, Ki, Kd, dt):
    """
    Implements a basic PID controller.
    
    Args:
        setpoint (float): The desired value or target.
        feedback (float): The measured or current value.
        Kp (float): The proportional gain.
        Ki (float): The integral gain.
        Kd (float): The derivative gain.
        dt (float): The time step or sample time.
    
    Returns:
        float: The control output.
    """
    # Calculate the error
    error = setpoint - feedback
    
    # Proportional term
    p_term = Kp * error
    
    # Integral term
    global integral
    integral += error * dt
    i_term = Ki * integral
    
    # Derivative term
    global previous_error
    derivative = (error - previous_error) / dt
    d_term = Kd * derivative
    previous_error = error
    
    # Calculate the total control output
    output = p_term + i_term + d_term
    
    # Ensure output is an integer and set to 0 if less than 0
    output = max(0, round(output))
    
    return output

# Thiết lập các tham số PID
Kp = 1
Ki = 0.1
Kd = 0.01
dt = 1  # thời gian lấy mẫu

# Thiết lập feedback
feedback = 0.03

# Thay đổi setpoint liên tục
setpoint = 0.01
setpoint_direction = 1  # 1 tăng, -1 giảm
while True:
    output = pid_controller(setpoint, feedback, Kp, Ki, Kd, dt)
    print(f"Setpoint: {setpoint}, Feedback: {feedback}, Output: {output}")
    
    # Thay đổi setpoint
    setpoint += 0.01 * setpoint_direction
    
    # Đảo hướng setpoint khi đạt đến giới hạn
    if setpoint >= 0.09:
        setpoint_direction = -1
    elif setpoint <= 0.01:
        setpoint_direction = 1
