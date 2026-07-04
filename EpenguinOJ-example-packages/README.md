# Tạo thông tin cho 1 package EPenguinOJ

(Sắp tới sẽ có phần dành cho polygon)

Thông tin cơ bản cho file .yml
```yml
time_limit: 2000
memory_limit: 512
```

Các file code khác:
```yml
answer: answer # Bắt buộc nếu sử dụng generators
checker: checker
validator: validator # Bắt buộc có nếu sử dụng hack
```

Testcases có sẵn bằng file
```yml
testcases:
  1.in 1.out
  2.in 2.out
  3.in 3.out
```

Testcases được tạo bởi generator
```yml
generators:
  gens/1: 10
  gens/1_pos: 10
  gens/1_neg: 10
  <file_gen>: <amounts> <seed>
```

Tạo các batches
```yml
batches:
  1:
    score: 10
    generators:
      gens/1: 10 1
      gens/1_pos: 10 2
      gens/1_neg: 10 3
  2:
    score: 10
    generators:
      gens/2: 10 6
      gens/2_pos: 10 7
      gens/2_neg: 10 36
  3:
    score: 10
    testcases:
      67.in 67.in
      36.in 36.out
```