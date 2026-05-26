x = 0
y = 10
L1:
if x < y goto L4
goto L3
L4:
if x != 5 goto L2
goto L3
L2:
if a == b goto L5
goto L8
L8:
if c == d goto L5
goto L6
L5:
t1 = x + 1
x = t1
goto L7
L6:
t2 = x + 2
x = t2
L7:
goto L1
L3:
if x == 5 goto L9
goto L10
L9:
t3 = y - 1
y = t3
goto L11
L10:
t4 = y + 1
y = t4
L11: