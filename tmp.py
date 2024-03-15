import random

group_of_items = ['a', 'b', 'c', 'd', 'e']  # A set or sequence will work here
num_to_select = 3  # Set the number of items to select
list_of_random_items = random.sample(group_of_items, num_to_select)

# Access the randomly selected items
first_random_item = list_of_random_items[0]
second_random_item = list_of_random_items[1]
join_list = ''.join(list_of_random_items)

print(f"Randomly selected items: {first_random_item}, {second_random_item}")
print(f"joined list: {join_list}")
