variableValue("position", "p6").
variableValue("position", "p2").
variableValue("position", "p7").
variableValue("position", "p5").
variableValue("position", "p1").
variableValue("position", "p3").
variableValue("position", "p4").
variableValue("position", "p0").
variableValue("broken-leg()", "trueValue").
variableValue("broken-leg()", "falseValue").
variableValue("up()", "trueValue").
variableValue("up()", "falseValue").

init("position", "p0").
init("broken-leg()", "falseValue").
init("up()", "falseValue").

goal(conj(conj(yest(yest(yest(yest(yest(has_value("position","p0")))))),since(has_value("position","p0"),has_value("position","p1"))),has_value("up()","trueValue"))).

action("jump-over_p3_p4_p5").
prec("jump-over_p3_p4_p5", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p3")))).
effect("jump-over_p3_p4_p5", "jump-over_p3_p4_p5_effect_0").
effect("jump-over_p3_p4_p5", "jump-over_p3_p4_p5_effect_1").
effect("jump-over_p3_p4_p5", "jump-over_p3_p4_p5_effect_2").
effect("jump-over_p3_p4_p5", "jump-over_p3_p4_p5_effect_3").
effect("jump-over_p3_p4_p5", "jump-over_p3_p4_p5_effect_4").
effect("jump-over_p3_p4_p5", "jump-over_p3_p4_p5_effect_5").
action("walk-right_p3_p4").
prec("walk-right_p3_p4", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p3")))).
effect("walk-right_p3_p4", "walk-right_p3_p4_effect_0").
action("jump-over_p4_p5_p6").
prec("jump-over_p4_p5_p6", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p4")))).
effect("jump-over_p4_p5_p6", "jump-over_p4_p5_p6_effect_0").
effect("jump-over_p4_p5_p6", "jump-over_p4_p5_p6_effect_1").
effect("jump-over_p4_p5_p6", "jump-over_p4_p5_p6_effect_2").
effect("jump-over_p4_p5_p6", "jump-over_p4_p5_p6_effect_3").
effect("jump-over_p4_p5_p6", "jump-over_p4_p5_p6_effect_4").
effect("jump-over_p4_p5_p6", "jump-over_p4_p5_p6_effect_5").
action("walk-left_p2_p1").
prec("walk-left_p2_p1", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p2")))).
effect("walk-left_p2_p1", "walk-left_p2_p1_effect_0").
action("walk-on-beam_p6_p7").
prec("walk-on-beam_p6_p7", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p6")))).
effect("walk-on-beam_p6_p7", "walk-on-beam_p6_p7_effect_0").
effect("walk-on-beam_p6_p7", "walk-on-beam_p6_p7_effect_1").
action("walk-on-beam_p4_p5").
prec("walk-on-beam_p4_p5", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p4")))).
effect("walk-on-beam_p4_p5", "walk-on-beam_p4_p5_effect_0").
effect("walk-on-beam_p4_p5", "walk-on-beam_p4_p5_effect_1").
action("jump-over_p2_p3_p4").
prec("jump-over_p2_p3_p4", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p2")))).
effect("jump-over_p2_p3_p4", "jump-over_p2_p3_p4_effect_0").
effect("jump-over_p2_p3_p4", "jump-over_p2_p3_p4_effect_1").
effect("jump-over_p2_p3_p4", "jump-over_p2_p3_p4_effect_2").
effect("jump-over_p2_p3_p4", "jump-over_p2_p3_p4_effect_3").
effect("jump-over_p2_p3_p4", "jump-over_p2_p3_p4_effect_4").
effect("jump-over_p2_p3_p4", "jump-over_p2_p3_p4_effect_5").
action("climb-down_").
prec("climb-down_", conj(has_value("up()","trueValue"),neg(has_value("broken-leg()","trueValue")))).
effect("climb-down_", "climb-down__effect_0").
action("walk-left_p4_p3").
prec("walk-left_p4_p3", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p4")))).
effect("walk-left_p4_p3", "walk-left_p4_p3_effect_0").
action("jump-over_p0_p1_p2").
prec("jump-over_p0_p1_p2", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p0")))).
effect("jump-over_p0_p1_p2", "jump-over_p0_p1_p2_effect_0").
effect("jump-over_p0_p1_p2", "jump-over_p0_p1_p2_effect_1").
effect("jump-over_p0_p1_p2", "jump-over_p0_p1_p2_effect_2").
effect("jump-over_p0_p1_p2", "jump-over_p0_p1_p2_effect_3").
effect("jump-over_p0_p1_p2", "jump-over_p0_p1_p2_effect_4").
effect("jump-over_p0_p1_p2", "jump-over_p0_p1_p2_effect_5").
action("walk-on-beam_p2_p3").
prec("walk-on-beam_p2_p3", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p2")))).
effect("walk-on-beam_p2_p3", "walk-on-beam_p2_p3_effect_0").
effect("walk-on-beam_p2_p3", "walk-on-beam_p2_p3_effect_1").
action("walk-right_p5_p6").
prec("walk-right_p5_p6", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p5")))).
effect("walk-right_p5_p6", "walk-right_p5_p6_effect_0").
action("walk-on-beam_p3_p4").
prec("walk-on-beam_p3_p4", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p3")))).
effect("walk-on-beam_p3_p4", "walk-on-beam_p3_p4_effect_0").
effect("walk-on-beam_p3_p4", "walk-on-beam_p3_p4_effect_1").
action("jump-over_p5_p6_p7").
prec("jump-over_p5_p6_p7", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p5")))).
effect("jump-over_p5_p6_p7", "jump-over_p5_p6_p7_effect_0").
effect("jump-over_p5_p6_p7", "jump-over_p5_p6_p7_effect_1").
effect("jump-over_p5_p6_p7", "jump-over_p5_p6_p7_effect_2").
effect("jump-over_p5_p6_p7", "jump-over_p5_p6_p7_effect_3").
effect("jump-over_p5_p6_p7", "jump-over_p5_p6_p7_effect_4").
effect("jump-over_p5_p6_p7", "jump-over_p5_p6_p7_effect_5").
action("walk-left_p1_p0").
prec("walk-left_p1_p0", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p1")))).
effect("walk-left_p1_p0", "walk-left_p1_p0_effect_0").
action("walk-left_p6_p5").
prec("walk-left_p6_p5", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p6")))).
effect("walk-left_p6_p5", "walk-left_p6_p5_effect_0").
action("walk-left_p5_p4").
prec("walk-left_p5_p4", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p5")))).
effect("walk-left_p5_p4", "walk-left_p5_p4_effect_0").
action("jump-over_p1_p2_p3").
prec("jump-over_p1_p2_p3", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p1")))).
effect("jump-over_p1_p2_p3", "jump-over_p1_p2_p3_effect_0").
effect("jump-over_p1_p2_p3", "jump-over_p1_p2_p3_effect_1").
effect("jump-over_p1_p2_p3", "jump-over_p1_p2_p3_effect_2").
effect("jump-over_p1_p2_p3", "jump-over_p1_p2_p3_effect_3").
effect("jump-over_p1_p2_p3", "jump-over_p1_p2_p3_effect_4").
effect("jump-over_p1_p2_p3", "jump-over_p1_p2_p3_effect_5").
action("walk-left_p3_p2").
prec("walk-left_p3_p2", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p3")))).
effect("walk-left_p3_p2", "walk-left_p3_p2_effect_0").
action("walk-on-beam_p0_p1").
prec("walk-on-beam_p0_p1", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p0")))).
effect("walk-on-beam_p0_p1", "walk-on-beam_p0_p1_effect_0").
effect("walk-on-beam_p0_p1", "walk-on-beam_p0_p1_effect_1").
action("walk-right_p4_p5").
prec("walk-right_p4_p5", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p4")))).
effect("walk-right_p4_p5", "walk-right_p4_p5_effect_0").
action("walk-left_p7_p6").
prec("walk-left_p7_p6", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p7")))).
effect("walk-left_p7_p6", "walk-left_p7_p6_effect_0").
action("walk-right_p2_p3").
prec("walk-right_p2_p3", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p2")))).
effect("walk-right_p2_p3", "walk-right_p2_p3_effect_0").
action("walk-right_p0_p1").
prec("walk-right_p0_p1", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p0")))).
effect("walk-right_p0_p1", "walk-right_p0_p1_effect_0").
action("walk-on-beam_p1_p2").
prec("walk-on-beam_p1_p2", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p1")))).
effect("walk-on-beam_p1_p2", "walk-on-beam_p1_p2_effect_0").
effect("walk-on-beam_p1_p2", "walk-on-beam_p1_p2_effect_1").
action("walk-right_p6_p7").
prec("walk-right_p6_p7", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p6")))).
effect("walk-right_p6_p7", "walk-right_p6_p7_effect_0").
action("climb_p0").
prec("climb_p0", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p0")))).
effect("climb_p0", "climb_p0_effect_0").
action("walk-right_p1_p2").
prec("walk-right_p1_p2", conj(neg(has_value("broken-leg()","trueValue")),conj(neg(has_value("up()","trueValue")),has_value("position","p1")))).
effect("walk-right_p1_p2", "walk-right_p1_p2_effect_0").
action("walk-on-beam_p5_p6").
prec("walk-on-beam_p5_p6", conj(neg(has_value("broken-leg()","trueValue")),conj(has_value("up()","trueValue"),has_value("position","p5")))).
effect("walk-on-beam_p5_p6", "walk-on-beam_p5_p6_effect_0").
effect("walk-on-beam_p5_p6", "walk-on-beam_p5_p6_effect_1").

add("jump-over_p2_p3_p4_effect_5", "position", "p4").
del("jump-over_p2_p3_p4_effect_5", "position", "p2").
add("jump-over_p3_p4_p5_effect_0", "broken-leg()", "trueValue").
del("jump-over_p3_p4_p5_effect_0", "broken-leg()", "falseValue").
del("jump-over_p3_p4_p5_effect_0", "up()", "trueValue").
add("jump-over_p3_p4_p5_effect_0", "up()", "falseValue").
add("jump-over_p3_p4_p5_effect_1", "broken-leg()", "trueValue").
del("jump-over_p3_p4_p5_effect_1", "broken-leg()", "falseValue").
add("jump-over_p3_p4_p5_effect_1", "position", "p4").
del("jump-over_p3_p4_p5_effect_1", "up()", "trueValue").
add("jump-over_p3_p4_p5_effect_1", "up()", "falseValue").
del("jump-over_p3_p4_p5_effect_1", "position", "p3").
add("jump-over_p1_p2_p3_effect_3", "broken-leg()", "trueValue").
del("jump-over_p1_p2_p3_effect_3", "broken-leg()", "falseValue").
add("jump-over_p1_p2_p3_effect_3", "position", "p3").
del("jump-over_p1_p2_p3_effect_3", "up()", "trueValue").
add("jump-over_p1_p2_p3_effect_3", "up()", "falseValue").
del("jump-over_p1_p2_p3_effect_3", "position", "p1").
add("walk-right_p6_p7_effect_0", "position", "p7").
del("walk-right_p6_p7_effect_0", "position", "p6").
add("walk-on-beam_p1_p2_effect_1", "position", "p2").
del("walk-on-beam_p1_p2_effect_1", "up()", "trueValue").
add("walk-on-beam_p1_p2_effect_1", "up()", "falseValue").
del("walk-on-beam_p1_p2_effect_1", "position", "p1").
add("walk-on-beam_p2_p3_effect_0", "position", "p3").
del("walk-on-beam_p2_p3_effect_0", "position", "p2").
add("jump-over_p1_p2_p3_effect_0", "broken-leg()", "trueValue").
del("jump-over_p1_p2_p3_effect_0", "broken-leg()", "falseValue").
del("jump-over_p1_p2_p3_effect_0", "up()", "trueValue").
add("jump-over_p1_p2_p3_effect_0", "up()", "falseValue").
del("climb-down__effect_0", "up()", "trueValue").
add("climb-down__effect_0", "up()", "falseValue").
add("jump-over_p5_p6_p7_effect_5", "position", "p7").
del("jump-over_p5_p6_p7_effect_5", "position", "p5").
add("jump-over_p0_p1_p2_effect_0", "broken-leg()", "trueValue").
del("jump-over_p0_p1_p2_effect_0", "broken-leg()", "falseValue").
del("jump-over_p0_p1_p2_effect_0", "up()", "trueValue").
add("jump-over_p0_p1_p2_effect_0", "up()", "falseValue").
add("walk-left_p4_p3_effect_0", "position", "p3").
del("walk-left_p4_p3_effect_0", "position", "p4").
add("walk-right_p5_p6_effect_0", "position", "p6").
del("walk-right_p5_p6_effect_0", "position", "p5").
add("jump-over_p5_p6_p7_effect_4", "position", "p7").
del("jump-over_p5_p6_p7_effect_4", "up()", "trueValue").
add("jump-over_p5_p6_p7_effect_4", "up()", "falseValue").
del("jump-over_p5_p6_p7_effect_4", "position", "p5").
add("walk-right_p1_p2_effect_0", "position", "p2").
del("walk-right_p1_p2_effect_0", "position", "p1").
add("walk-on-beam_p4_p5_effect_0", "position", "p5").
del("walk-on-beam_p4_p5_effect_0", "position", "p4").
add("walk-left_p6_p5_effect_0", "position", "p5").
del("walk-left_p6_p5_effect_0", "position", "p6").
add("jump-over_p1_p2_p3_effect_1", "broken-leg()", "trueValue").
del("jump-over_p1_p2_p3_effect_1", "broken-leg()", "falseValue").
add("jump-over_p1_p2_p3_effect_1", "position", "p2").
del("jump-over_p1_p2_p3_effect_1", "up()", "trueValue").
add("jump-over_p1_p2_p3_effect_1", "up()", "falseValue").
del("jump-over_p1_p2_p3_effect_1", "position", "p1").
add("walk-right_p0_p1_effect_0", "position", "p1").
del("walk-right_p0_p1_effect_0", "position", "p0").
add("jump-over_p3_p4_p5_effect_3", "broken-leg()", "trueValue").
del("jump-over_p3_p4_p5_effect_3", "broken-leg()", "falseValue").
add("jump-over_p3_p4_p5_effect_3", "position", "p5").
del("jump-over_p3_p4_p5_effect_3", "up()", "trueValue").
add("jump-over_p3_p4_p5_effect_3", "up()", "falseValue").
del("jump-over_p3_p4_p5_effect_3", "position", "p3").
add("walk-left_p1_p0_effect_0", "position", "p0").
del("walk-left_p1_p0_effect_0", "position", "p1").
add("walk-right_p4_p5_effect_0", "position", "p5").
del("walk-right_p4_p5_effect_0", "position", "p4").
add("walk-on-beam_p3_p4_effect_1", "position", "p4").
del("walk-on-beam_p3_p4_effect_1", "up()", "trueValue").
add("walk-on-beam_p3_p4_effect_1", "up()", "falseValue").
del("walk-on-beam_p3_p4_effect_1", "position", "p3").
add("walk-on-beam_p0_p1_effect_0", "position", "p1").
del("walk-on-beam_p0_p1_effect_0", "position", "p0").
add("walk-left_p3_p2_effect_0", "position", "p2").
del("walk-left_p3_p2_effect_0", "position", "p3").
add("jump-over_p1_p2_p3_effect_4", "position", "p3").
del("jump-over_p1_p2_p3_effect_4", "up()", "trueValue").
add("jump-over_p1_p2_p3_effect_4", "up()", "falseValue").
del("jump-over_p1_p2_p3_effect_4", "position", "p1").
add("jump-over_p2_p3_p4_effect_3", "broken-leg()", "trueValue").
del("jump-over_p2_p3_p4_effect_3", "broken-leg()", "falseValue").
add("jump-over_p2_p3_p4_effect_3", "position", "p4").
del("jump-over_p2_p3_p4_effect_3", "up()", "trueValue").
add("jump-over_p2_p3_p4_effect_3", "up()", "falseValue").
del("jump-over_p2_p3_p4_effect_3", "position", "p2").
add("jump-over_p0_p1_p2_effect_1", "broken-leg()", "trueValue").
del("jump-over_p0_p1_p2_effect_1", "broken-leg()", "falseValue").
add("jump-over_p0_p1_p2_effect_1", "position", "p1").
del("jump-over_p0_p1_p2_effect_1", "up()", "trueValue").
add("jump-over_p0_p1_p2_effect_1", "up()", "falseValue").
del("jump-over_p0_p1_p2_effect_1", "position", "p0").
add("jump-over_p5_p6_p7_effect_2", "position", "p6").
del("jump-over_p5_p6_p7_effect_2", "up()", "trueValue").
add("jump-over_p5_p6_p7_effect_2", "up()", "falseValue").
del("jump-over_p5_p6_p7_effect_2", "position", "p5").
add("walk-left_p7_p6_effect_0", "position", "p6").
del("walk-left_p7_p6_effect_0", "position", "p7").
add("jump-over_p4_p5_p6_effect_5", "position", "p6").
del("jump-over_p4_p5_p6_effect_5", "position", "p4").
add("jump-over_p2_p3_p4_effect_1", "broken-leg()", "trueValue").
del("jump-over_p2_p3_p4_effect_1", "broken-leg()", "falseValue").
add("jump-over_p2_p3_p4_effect_1", "position", "p3").
del("jump-over_p2_p3_p4_effect_1", "up()", "trueValue").
add("jump-over_p2_p3_p4_effect_1", "up()", "falseValue").
del("jump-over_p2_p3_p4_effect_1", "position", "p2").
add("jump-over_p0_p1_p2_effect_2", "position", "p1").
del("jump-over_p0_p1_p2_effect_2", "up()", "trueValue").
add("jump-over_p0_p1_p2_effect_2", "up()", "falseValue").
del("jump-over_p0_p1_p2_effect_2", "position", "p0").
add("jump-over_p2_p3_p4_effect_4", "position", "p4").
del("jump-over_p2_p3_p4_effect_4", "up()", "trueValue").
add("jump-over_p2_p3_p4_effect_4", "up()", "falseValue").
del("jump-over_p2_p3_p4_effect_4", "position", "p2").
add("jump-over_p4_p5_p6_effect_1", "broken-leg()", "trueValue").
del("jump-over_p4_p5_p6_effect_1", "broken-leg()", "falseValue").
add("jump-over_p4_p5_p6_effect_1", "position", "p5").
del("jump-over_p4_p5_p6_effect_1", "up()", "trueValue").
add("jump-over_p4_p5_p6_effect_1", "up()", "falseValue").
del("jump-over_p4_p5_p6_effect_1", "position", "p4").
add("jump-over_p2_p3_p4_effect_0", "broken-leg()", "trueValue").
del("jump-over_p2_p3_p4_effect_0", "broken-leg()", "falseValue").
del("jump-over_p2_p3_p4_effect_0", "up()", "trueValue").
add("jump-over_p2_p3_p4_effect_0", "up()", "falseValue").
add("jump-over_p5_p6_p7_effect_0", "broken-leg()", "trueValue").
del("jump-over_p5_p6_p7_effect_0", "broken-leg()", "falseValue").
del("jump-over_p5_p6_p7_effect_0", "up()", "trueValue").
add("jump-over_p5_p6_p7_effect_0", "up()", "falseValue").
add("jump-over_p4_p5_p6_effect_4", "position", "p6").
del("jump-over_p4_p5_p6_effect_4", "up()", "trueValue").
add("jump-over_p4_p5_p6_effect_4", "up()", "falseValue").
del("jump-over_p4_p5_p6_effect_4", "position", "p4").
add("walk-on-beam_p3_p4_effect_0", "position", "p4").
del("walk-on-beam_p3_p4_effect_0", "position", "p3").
add("walk-on-beam_p6_p7_effect_1", "position", "p7").
del("walk-on-beam_p6_p7_effect_1", "up()", "trueValue").
add("walk-on-beam_p6_p7_effect_1", "up()", "falseValue").
del("walk-on-beam_p6_p7_effect_1", "position", "p6").
add("walk-right_p3_p4_effect_0", "position", "p4").
del("walk-right_p3_p4_effect_0", "position", "p3").
add("walk-on-beam_p2_p3_effect_1", "position", "p3").
del("walk-on-beam_p2_p3_effect_1", "up()", "trueValue").
add("walk-on-beam_p2_p3_effect_1", "up()", "falseValue").
del("walk-on-beam_p2_p3_effect_1", "position", "p2").
add("walk-on-beam_p1_p2_effect_0", "position", "p2").
del("walk-on-beam_p1_p2_effect_0", "position", "p1").
add("jump-over_p0_p1_p2_effect_3", "broken-leg()", "trueValue").
del("jump-over_p0_p1_p2_effect_3", "broken-leg()", "falseValue").
add("jump-over_p0_p1_p2_effect_3", "position", "p2").
del("jump-over_p0_p1_p2_effect_3", "up()", "trueValue").
add("jump-over_p0_p1_p2_effect_3", "up()", "falseValue").
del("jump-over_p0_p1_p2_effect_3", "position", "p0").
add("jump-over_p4_p5_p6_effect_3", "broken-leg()", "trueValue").
del("jump-over_p4_p5_p6_effect_3", "broken-leg()", "falseValue").
add("jump-over_p4_p5_p6_effect_3", "position", "p6").
del("jump-over_p4_p5_p6_effect_3", "up()", "trueValue").
add("jump-over_p4_p5_p6_effect_3", "up()", "falseValue").
del("jump-over_p4_p5_p6_effect_3", "position", "p4").
add("walk-on-beam_p6_p7_effect_0", "position", "p7").
del("walk-on-beam_p6_p7_effect_0", "position", "p6").
add("jump-over_p4_p5_p6_effect_2", "position", "p5").
del("jump-over_p4_p5_p6_effect_2", "up()", "trueValue").
add("jump-over_p4_p5_p6_effect_2", "up()", "falseValue").
del("jump-over_p4_p5_p6_effect_2", "position", "p4").
add("walk-right_p2_p3_effect_0", "position", "p3").
del("walk-right_p2_p3_effect_0", "position", "p2").
add("walk-on-beam_p4_p5_effect_1", "position", "p5").
del("walk-on-beam_p4_p5_effect_1", "up()", "trueValue").
add("walk-on-beam_p4_p5_effect_1", "up()", "falseValue").
del("walk-on-beam_p4_p5_effect_1", "position", "p4").
add("walk-on-beam_p0_p1_effect_1", "position", "p1").
del("walk-on-beam_p0_p1_effect_1", "up()", "trueValue").
add("walk-on-beam_p0_p1_effect_1", "up()", "falseValue").
del("walk-on-beam_p0_p1_effect_1", "position", "p0").
add("jump-over_p1_p2_p3_effect_2", "position", "p2").
del("jump-over_p1_p2_p3_effect_2", "up()", "trueValue").
add("jump-over_p1_p2_p3_effect_2", "up()", "falseValue").
del("jump-over_p1_p2_p3_effect_2", "position", "p1").
add("jump-over_p5_p6_p7_effect_3", "broken-leg()", "trueValue").
del("jump-over_p5_p6_p7_effect_3", "broken-leg()", "falseValue").
add("jump-over_p5_p6_p7_effect_3", "position", "p7").
del("jump-over_p5_p6_p7_effect_3", "up()", "trueValue").
add("jump-over_p5_p6_p7_effect_3", "up()", "falseValue").
del("jump-over_p5_p6_p7_effect_3", "position", "p5").
add("jump-over_p5_p6_p7_effect_1", "broken-leg()", "trueValue").
del("jump-over_p5_p6_p7_effect_1", "broken-leg()", "falseValue").
add("jump-over_p5_p6_p7_effect_1", "position", "p6").
del("jump-over_p5_p6_p7_effect_1", "up()", "trueValue").
add("jump-over_p5_p6_p7_effect_1", "up()", "falseValue").
del("jump-over_p5_p6_p7_effect_1", "position", "p5").
add("walk-left_p2_p1_effect_0", "position", "p1").
del("walk-left_p2_p1_effect_0", "position", "p2").
add("jump-over_p3_p4_p5_effect_2", "position", "p4").
del("jump-over_p3_p4_p5_effect_2", "up()", "trueValue").
add("jump-over_p3_p4_p5_effect_2", "up()", "falseValue").
del("jump-over_p3_p4_p5_effect_2", "position", "p3").
add("walk-on-beam_p5_p6_effect_1", "position", "p6").
del("walk-on-beam_p5_p6_effect_1", "up()", "trueValue").
add("walk-on-beam_p5_p6_effect_1", "up()", "falseValue").
del("walk-on-beam_p5_p6_effect_1", "position", "p5").
add("jump-over_p0_p1_p2_effect_4", "position", "p2").
del("jump-over_p0_p1_p2_effect_4", "up()", "trueValue").
add("jump-over_p0_p1_p2_effect_4", "up()", "falseValue").
del("jump-over_p0_p1_p2_effect_4", "position", "p0").
add("climb_p0_effect_0", "up()", "trueValue").
del("climb_p0_effect_0", "up()", "falseValue").
add("jump-over_p3_p4_p5_effect_5", "position", "p5").
del("jump-over_p3_p4_p5_effect_5", "position", "p3").
add("jump-over_p2_p3_p4_effect_2", "position", "p3").
del("jump-over_p2_p3_p4_effect_2", "up()", "trueValue").
add("jump-over_p2_p3_p4_effect_2", "up()", "falseValue").
del("jump-over_p2_p3_p4_effect_2", "position", "p2").
add("jump-over_p0_p1_p2_effect_5", "position", "p2").
del("jump-over_p0_p1_p2_effect_5", "position", "p0").
add("walk-left_p5_p4_effect_0", "position", "p4").
del("walk-left_p5_p4_effect_0", "position", "p5").
add("jump-over_p3_p4_p5_effect_4", "position", "p5").
del("jump-over_p3_p4_p5_effect_4", "up()", "trueValue").
add("jump-over_p3_p4_p5_effect_4", "up()", "falseValue").
del("jump-over_p3_p4_p5_effect_4", "position", "p3").
add("jump-over_p4_p5_p6_effect_0", "broken-leg()", "trueValue").
del("jump-over_p4_p5_p6_effect_0", "broken-leg()", "falseValue").
del("jump-over_p4_p5_p6_effect_0", "up()", "trueValue").
add("jump-over_p4_p5_p6_effect_0", "up()", "falseValue").
add("jump-over_p1_p2_p3_effect_5", "position", "p3").
del("jump-over_p1_p2_p3_effect_5", "position", "p1").
add("walk-on-beam_p5_p6_effect_0", "position", "p6").
del("walk-on-beam_p5_p6_effect_0", "position", "p5").
