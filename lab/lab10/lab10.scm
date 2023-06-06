(define (over-or-under num1 num2) 'YOUR-CODE-HERE
    (if (< num1 num2)
        -1
        (if (= num1 num2)
            0
            1
        )
    )   
)

(define (make-adder num) 'YOUR-CODE-HERE
    (lambda (inc) (+ num inc))    
)

(define (composed f g) 'YOUR-CODE-HERE
    (lambda (x) (f (g x)))    
)

(define lst
  		(cons (cons 1 nil)
  			  (cons 2
  			  	    (cons (cons 3 (cons 4 nil))
  			  	    	  (cons 5 nil)
  			  	    )
		  	  )
  		)
)

(define (duplicate lst) 'YOUR-CODE-HERE
    (if (null? lst)
        nil
        cons((car lst) cons((car lst) duplicate((cdr lst))))
    )
)
