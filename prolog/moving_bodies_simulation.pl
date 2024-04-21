% time steps into the future to calculate
time(1).

%   (B, Ix, Iy, IVx, IVy, Fx, Fy, M, T)
body(1, 0,  0,  0,   0,   1,  0,  1, 0).
%body(2, 0,  0,  0,   0,   0,  1,  1, 0).

% consolidated terms for input
body(B, Ix, Iy, IVx, IVy, Fx, Fy, M, T) :- body(B), initial_position_x(B, Ix), initial_position_y(B, Iy), initial_velocity_x(B, IVx), initial_velocity_y(B, IVy), force_x(B, Fx), force_y(B, Fy), mass(B, M), time(T). 

body(B) :- body(B, _, _, _, _, _, _, _, _).
initial_position_x(B, Ix) :- body(B, Ix, _, _, _, _, _, _, _).
initial_position_y(B, Iy) :- body(B, _, Iy, _, _, _, _, _, _).
initial_velocity_x(B, IVx) :- body(B, _, _, IVx, _, _, _, _, _).
initial_velocity_y(B, IVy) :- body(B, _, _, _, IVy, _, _, _, _).
force_x(B, Fx) :- body(B, _, _, _, _, Fx, _, _, _).
force_y(B, Fy) :- body(B, _, _, _, _, _, Fy, _, _).
mass(B, M) :- body(B, _, _, _, _, _, _, M, _).
time(T) :- body(_, _, _, _, _, _, _, _, T).

% Calculate acceleration from force and mass (F = ma, a = F/m) for both x and y components
acceleration_x(B, Ax) :- force_x(B, Fx), mass(B, M), Ax = Fx / M, body(B).
acceleration_y(B, Ay) :- force_y(B, Fy), mass(B, M), Ay = Fy / M, body(B).

% Calculate velocity at each time step for both x and y components
velocity_x(B, Vx, T+1) :- velocity_x(B, Vx0, T), acceleration_x(B, Ax), Vx = Vx0 + Ax, time(T), body(B).
velocity_y(B, Vy, T+1) :- velocity_y(B, Vy0, T), acceleration_y(B, Ay), Vy = Vy0 + Ay, time(T), body(B).

% Initialize velocity at time 0 for both x and y components
velocity_x(B, Vx, 0) :- initial_velocity_x(B, Vx), body(B).
velocity_y(B, Vy, 0) :- initial_velocity_y(B, Vy), body(B).

% Calculate position at each time step for both x and y components
position_x(B, Px, T+1) :- position_x(B, Px0, T), velocity_x(B, Vx, T+1), Px = Px0 + Vx, time(T), body(B).
position_y(B, Py, T+1) :- position_y(B, Py0, T), velocity_y(B, Vy, T+1), Py = Py0 + Vy, time(T), body(B).

% Initialize position at time 0 for both x and y components
position_x(B, Px, 0) :- initial_position_x(B, Px), body(B).
position_y(B, Py, 0) :- initial_position_y(B, Py), body(B).

% consolidated term for output for debugging
body(B, T, Px, Py, Vx, Vy, M) :- body(B), time(T), position_x(B, Px, T), position_y(B, Py, T), velocity_x(B, Vx, T), velocity_y(B, Vy, T), mass(B, M).

% just the basics for output
time_body_position(T, B, Px, Py) :- body(B), time(T), position_x(B, Px, T), position_y(B, Py, T), T > 0.

% Output the results for each time, body, and position
#show time_body_position/4.
