-- Document changes to Database schema caused by various changesets. These
-- commands should be run in MySQL "./manage.py dbshell". Sometimes a
-- "./manage.py syncdb" is needed to create new tables.
-- The hex string is the hg changeset that changed model.py and caused the
-- schema change.

[538cf862c100]
    ALTER TABLE `projects_projectstatusupdate` ADD COLUMN `report_id` integer NULL;
    ALTER TABLE `projects_projectstatusupdate` ADD CONSTRAINT report_id_refs_id_38612666 FOREIGN KEY (`report_id`) REFERENCES `projects_report` (`id`);
    CREATE INDEX `projects_projectstatusupdate_report_id` ON `projects_projectstatusupdate` (`report_id`);
    ./manage.py syncdb -- creates new table `projects_projectvisit`

[a7b257d19ac1]
    ALTER TABLE `donations_donation` ADD COLUMN `project_id` integer NULL;
    ALTER TABLE `donations_donation` ADD CONSTRAINT project_id_refs_id_39c39dd1 FOREIGN KEY (`project_id`) REFERENCES `projects_project` (`id`);
    CREATE INDEX `donations_donation_project_id` ON `donations_donation` (`project_id`);

[8451f4b7b909]
    ALTER TABLE `projects_disbursal`            ADD COLUMN `amount_inr` numeric(20, 4) NULL;
    ALTER TABLE `projects_projectfundingdetail` ADD COLUMN `budget_inr` numeric(20, 4) NULL;

[ffa239d4da09]
    ALTER TABLE `projects_projectstatusupdate`  ADD COLUMN `reject_reason` integer NULL;

[148a8f618e41]
    ALTER TABLE `donations_donation`  ADD COLUMN `project_subscription` bool NOT NULL;
    ALTER TABLE `donations_donation`  ADD COLUMN `event_subscription`   bool NOT NULL;
    ALTER TABLE `donations_donation`  ADD COLUMN `paper_receipt`        bool NOT NULL;
    ALTER TABLE `donations_htgsignup` ADD COLUMN `project_subscription` bool NOT NULL;
    ALTER TABLE `donations_htgsignup` ADD COLUMN `event_subscription` bool NOT NULL;
    ALTER TABLE `donations_htgsignup` ADD COLUMN `paper_receipt` bool NOT NULL;
