# Evoting
Evoting system for PEMIRA FISIKA UR 2020 by dasta

# System Overview

> for normal user

- user can login with pre defined username i.e username is student identification number (NIM)

- user can choose candidate and submit the chosen data to the database

- use can logout from current session

> for admin user

- admin can add student identification numbers from csv/txt files

- admin can add candidate data from the admin dashboard

# system flow on user

1. user login using predefined user id 
2. user clicked on the candidates (radio button)
3. user clicked vote
4. voting result shown on the user dashboard
5. user logged out from current session

# system flow on admin

1. admin login using predefined admin password
2. admin can add candidates info on the dashboard
3. admin can view and edit candidate info
4. admin can delete candidates
5. admin can view the final result of the voting process
6. admin can view the result of vote of particular candidate
7. admin can logout of current session

# database model

1. User

- id: int, primary key, autoincrement
- role: string
- nim: int

relation with candidates id

one user only can vote for one candidates

2. Candidates

# deployment

