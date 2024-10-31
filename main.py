import json
import requests
import sys
import mysql.connector as mysql
from datetime import date, datetime, timedelta

station = sys.argv[1]

API_RESPONSE = json.loads(
  requests.request(
    "GET",
    "https://dbf.finalrewind.org/{}.json?version=3".format(station)
  ).text
)["departures"]

connection = mysql.connect(
  host = "localhost",
  user = "delays",
  password = "test",
  database = "delays",
  port = 3306
)
cursor = connection.cursor()

stmts = {
  "create_table": """
      CREATE TABLE IF NOT EXISTS `delays`.`{}` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `trainNumber` MEDIUMINT NOT NULL,
        `line` TINYTEXT NOT NULL,
        `destination` TINYTEXT NOT NULL,
        `via` JSON NOT NULL,
        `isCancelled` BOOLEAN NOT NULL,
        `arrivalScheduled` TINYTEXT NOT NULL,
        `arrivalDelay` SMALLINT NOT NULL,
        `departureScheduled` TINYTEXT NOT NULL,
        `departureDelay` SMALLINT NOT NULL,
        `trackScheduled` SMALLINT NOT NULL,
        `trackUsed` SMALLINT NOT NULL,
        `firstAdded` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `lastUpdated` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`)
      );
    """,
  "check_train_exists": """
      SELECT `id` FROM `delays`.`{}`
      WHERE
        `trainNumber` = {}
      AND
        DATE(`firstAdded`) = '{}';
    """,
  "insert_train": """
      INSERT INTO `delays`.`{}`
        (`trainNumber`, `line`, `destination`, `via`, `isCancelled`, `arrivalScheduled`, `arrivalDelay`, `departureScheduled`, `departureDelay`, `trackScheduled`, `trackUsed`)
      VALUES
        ({},'{}','{}','{}',{},'{}',{},'{}',{},{},{});
    """,
  "update_train": """
      UPDATE `delays`.`{}` 
      SET
        `destination` = '{}',
        `via` = '{}',
        `arrivalDelay` = {},
        `departureDelay` = {},
        `isCancelled` = {},
        `trackUsed` = {}
      WHERE
        `trainNumber` = {}
      AND
        DATE(`firstAdded`) = '{}';
    """
}

cursor.execute(stmts.get("create_table").format(station))

for item in API_RESPONSE:
  trainNumber = item["trainNumber"]
  line = item["train"]
  destination = item["destination"]
  via = item["via"]
  isCancelled = item["isCancelled"]

  # scheduled values may be None if a train starts or terminates at a station
  arrivalScheduled = item["scheduledArrival"] if not item["scheduledArrival"] == None else "-1"
  departureScheduled = item["scheduledDeparture"] if not item["scheduledDeparture"] == None else "-1"

  # delay values may be empty / None if a train is on time for once
  arrivalDelay = item["delayArrival"] if not item["delayArrival"] == None else 0
  departureDelay = item["delayDeparture"] if not item["delayDeparture"] == None else 0

  # track values may be non existent due to rail replacement service
  trackScheduled = -1
  trackUsed = -1
  if not ("Bus" in line):
    if item["scheduledPlatform"]:
      trackScheduled = item["scheduledPlatform"]
    if item["platform"]:
      trackUsed = item["platform"]
  print(trainNumber, line, destination, via, isCancelled, arrivalScheduled, arrivalDelay, departureScheduled, departureDelay, trackScheduled, trackUsed)


  action = cursor.execute(stmts.get("check_train_exists").format(station, trainNumber, date.today()))
  result = cursor.fetchall()
  if (len(result) == 0):
    hour = int(arrivalScheduled[:2]) if not arrivalScheduled == "-1" else int(departureScheduled[:2])
    now = datetime.now()
    if not((now.hour > 20) and (hour in range(0,4))):
      action = cursor.execute(stmts.get("insert_train").format(station, trainNumber, line, destination, str(via).replace("'", "\""), isCancelled, arrivalScheduled, arrivalDelay, departureScheduled, departureDelay, trackScheduled, trackUsed))
      connection.commit()
  else:
    action = cursor.execute(stmts.get("update_train").format(station, destination, str(via).replace("'", "\""), arrivalDelay, departureDelay, isCancelled, trackUsed, trainNumber, date.today()))
    connection.commit()