# Visualize your data with Grafana.

1. Download and install Grafana from https://grafana.com/grafana/download
2. Open Grafana dashboard by using your favourite browser http://localhost:3000
3. Login by username: "admin" & password "admin"
4. Optionally change your password.
5. Join your data source: choose MySQL, fill in:
host: my was by deafalt located on the address 0.0.0.0:3306 (should work localhost:3306)
database: coffee_database
user: root
password: root
check "skip TLS verify"
max open: 0
max idle: 2
max lifetime: 14400
max time interval: 1m

Save & test.
6. Create new dashboard.
7. Create new panel.
8. Add query, click edit SQL, paste this:
SELECT  NOW() AS "time", g.GrindName AS metric, r.Count AS value
FROM Records r, Grinds g
WHERE g.ID = r.ID
ORDER BY r.ID

9. Set format as: Timeseries
10. On visualization tab set x-axis mode: series (in this step you should see nice bar chart)
11. Optionally set other parameters.
12. Save.
