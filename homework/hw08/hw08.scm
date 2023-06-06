(define (my-filter pred s) 'YOUR-CODE-HERE
  (if (null? s)
    nil
    (if (pred (car s))
      (cons (car s) (my-filter pred (cdr s)))
      (my-filter pred (cdr s))
    )
  )
)

(define (interleave lst1 lst2) 'YOUR-CODE-HERE
  (if (null? lst1)
    lst2
    (if (null? lst2)
      lst1
      (cons (car lst1) (cons (car lst2) (interleave (cdr lst1) (cdr lst2))))
    )
  )
)

(define (accumulate joiner start n term)
  'YOUR-CODE-HERE
  (if (< n 1)
    start
    (accumulate joiner (joiner start (term n)) (- n 1) term)
  )
)

(define (no-repeats lst) 'YOUR-CODE-HERE
  (if (null? lst) lst
    (cons (car lst) 
    (no-repeats (my-filter (lambda (x) (not (= x (car lst)))) lst))))
)
