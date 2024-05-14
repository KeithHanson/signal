%    (B, Ix, Iy, IVx, IVy, Fx, Fy, M, T)
%body(1, 0,  0,  0,   0,   1,  0,  1, 0).
%bod (4, 0, 0,   0,  -1,   0,  1,  1, 0).

%Define the maximum velocity, split this out into it's own program and parameterize it
max_velocity(1).

% Apply thrust north if velocity in y direction is less than -max_velocity
command("thrust n") :- body(_, _, _, _, VY, _, _, _, _), max_velocity(Max), VY < -Max.
command("thrust n") :- body(_, _, _, _, VY, _, Fy, _, _), max_velocity(Max), VY <= -Max, Fy < 0.
command("thrust reset") :- body(_, _, _, _, VY, _, Fy, _, _), max_velocity(Max), VY = -Max, Fy > 0.

% Apply thrust south if velocity in y direction is greater than max_velocity, or if we need to stop thrusting north
command("thrust s") :- body(_, _, _, _, VY, _, _, _, _), max_velocity(Max), VY > Max.
command("thrust s") :- body(_, _, _, _, VY, _, Fy, _, _), max_velocity(Max), VY >= Max, Fy > 0.
command("thrust reset") :- body(_, _, _, _, VY, _, Fy, _, _), max_velocity(Max), VY = Max, Fy < 0.

% Apply thrust east if velocity in x direction is less than -max_velocity
command("thrust e") :- body(_, _, _, VX, _, _, _, _, _), max_velocity(Max), VX < -Max.
command("thrust e") :- body(_, _, _, VX, _, Fx, _, _, _), max_velocity(Max), VX <= -Max, Fx < 0.
command("thrust reset") :- body(_, _, _, VX, _, Fx, _, _, _), max_velocity(Max), VX = -Max, Fx > 0.

% Apply thrust west if velocity in x direction is greater than max_velocity
command("thrust w") :- body(_, _, _, VX, _, _, _, _, _), max_velocity(Max), VX > Max.
command("thrust w") :- body(_, _, _, VX, _, Fx, _, _, _), max_velocity(Max), VX >= Max, Fx > 0.
command("thrust reset") :- body(_, _, _, VX, _, Fx, _, _, _), max_velocity(Max), VX = Max, Fx < 0.

% Output the thrust commands
#show command/1.
