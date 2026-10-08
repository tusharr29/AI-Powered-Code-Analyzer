def process_numbers(numbers):
    total = 0
    unused_value = 10
    for i in range(len(numbers)):
        if numbers[i] > 0:
            if numbers[i] % 2 == 0:
                total += numbers[i]
            else:
                total += numbers[i] * 2
    return total

while True:
    print(process_numbers([1, 2, 3]))
