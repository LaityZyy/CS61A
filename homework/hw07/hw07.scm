(define (cddr s) (cdr (cdr s)))

(define (cadr s) 'YOUR-CODE-HERE (car (cdr s)))

(define (caddr s) 'YOUR-CODE-HERE (car (cddr s)))

(define (ascending? asc-lst) 'YOUR-CODE-HERE
  (if (or (null? asc-lst) (null? (cdr asc-lst)))
  #t
  (if (<= (car asc-lst) (cadr asc-lst))
   (ascending? (cdr asc-lst))
   #f))
)

(define (square n) (* n n))

(define (pow base exp) 'YOUR-CODE-HERE
   (if (= exp 0)
    1
    (if (even? exp)
    (pow (square base) (/ exp 2))
    (* base (pow (square base) (/ (- exp 1) 2)))
    )
   )    
)