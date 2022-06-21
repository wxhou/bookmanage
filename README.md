# 图书管理系统


# step1
pybabel extract -F babel.cfg -o messages.pot .

# step2
pybabel update -i messages.pot -d translations

# step3
pybabel compile -d translations