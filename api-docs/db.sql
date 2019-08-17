CREATE TABLE `Users`
(
  `id` int PRIMARY KEY,
  `firstname` varchar(255) NOT NULL,
  `lastname` varchar(255) NOT NULL,
  `gender` varchar(255) NOT NULL,
  `tokens` int NOT NULL,
  `total_force` int,
  `punch_count` int
);

CREATE TABLE `Workouts`
(
  `id` int PRIMARY KEY,
  `title` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `start_time` datetime NOT NULL,
  `max_users` int
);

CREATE TABLE `Punches`
(
  `id` int PRIMARY KEY,
  `user_id` int,
  `time_stamp` datetime NOT NULL,
  `force` int NOT NULL
);

CREATE TABLE `Bookings`
(
  `id` int PRIMARY KEY,
  `user_id` int,
  `workout_id` int
);

ALTER TABLE `Punches` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`);

ALTER TABLE `Bookings` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`);

ALTER TABLE `Bookings` ADD FOREIGN KEY (`workout_id`) REFERENCES `Workouts` (`id`);

