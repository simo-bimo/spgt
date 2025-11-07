
(define (problem coffee1)
   (:domain robot_coffee)
   (:objects lab office1 office2 office3 office4 office5 - office
             kitch - kitchen)
   (:init (robotat lab)
          (connected lab office1)
          (connected office1 lab)
          (connected kitch office1)
          (connected office1 kitch)
          (connected office1 office2)
          (connected office2 office1)
          (connected office1 office3)
          (connected office3 office1)
          (connected office1 office4)
          (connected office4 office1)
          (connected office1 office5)
(connected office5 office1)

          (connected office2 office3)
          (connected office3 office2)
          (connected office3 office4)
          (connected office4 office3)
          (connected office4 office5)
(connected office5 office4))

	(:goal (and (coffeeat office1))
	; Run with --goal="((!(robotat=office1))S(coffeeat(office1)=trueValue))&Y(coffeeat(office1)=trueValue))"
	; for the temporal objective from the thesis.
)

)