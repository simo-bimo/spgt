(define (domain robot_coffee)
  (:requirements :strips :non-deterministic :typing)
 
  (:types office - room
	kitchen - room
  )
(:predicates (robotat ?x - room)
	     (coffeeat ?x - room)
	     (connected ?x - room ?y - room)
	     (has_coffee)
             )

(:action move
  :parameters
   (?x - room
    ?y - room)
  :precondition
   (and
   (robotat ?x) (connected ?x ?y))
  :effect
   (and
   (robotat ?y) (not (robotat ?x)))
)

(:action prepare_coffee
  :parameters
   (?x - kitchen)
  :precondition
   (and
   (robotat ?x) (not (has_coffee)))
  :effect
   (has_coffee)
)

(:action put_coffee
  :parameters
   (?x - office)
  :precondition
   (and
   (robotat ?x) (has_coffee))
  :effect
   (oneof 
     (and (not (has_coffee)) (coffeeat ?x))
     (and (not (has_coffee)))
   )

)

)