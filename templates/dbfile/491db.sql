
CREATE TABLE [HospitalSystemRegion]
(
      [HospitalSystemRegionID] int PRIMARY KEY,
      [HospitalSystemID] int,
      [RegionName] varchar(MAX)
)
GO

CREATE TABLE [HospitalSystem]
(
      [HospitalSystemID] int PRIMARY KEY,
      [HospitalSystemName] varchar(MAX)
)
GO

CREATE TABLE [ScheduleFrequency]
(
      [ScheduleFrequencyID] int PRIMARY KEY,
      [ScheduleFrequencyDescription] varchar(50),
      [Active] bit
)
GO

CREATE TABLE [SchedulePeriod]
(
      [SchedulePeriodID] int PRIMARY KEY,
      [SchedulePeriodDescription] varchar(50)
)
GO

CREATE TABLE [ScheduleTask]
(
      [ScheduleTaskID] int PRIMARY KEY,
      [ScheduleTaskDesc] varchar(MAX),
      [Active] bit
)
GO

CREATE TABLE [Scheduler]
(
      [ScheduleID] int PRIMARY KEY,
      [ScheduleTaskID] int,
      [HospitalSystemRegionID] int,
      [ScheduleFrequencyID] int,
      [SchedulePeriodID] int,
      [FileID] int
)
GO

CREATE TABLE [Recipients]
(
      [RecipientsID] int PRIMARY KEY,
      [ScheduleID] int,
      [UserID] int,
      [Active] bit
)
GO

CREATE TABLE [User]
(
      [UserID] int PRIMARY KEY,
      [UserName] varchar(MAX),
      [UserEmail] varchar(MAX),
      [UserPassword] varchar(50),
      [HospitalSystemRegionID] int,
      [RoleID] int
)
GO

CREATE TABLE [File]
(
      [FileID] int PRIMARY KEY,
      [FileName] varchar(50),
      [FilePath] varchar(100),
      [HospitalSystemRegionID] int
)
GO

CREATE TABLE [Role]
(
      [RoleID] int PRIMARY KEY,
      [RoleName] varchar(50)
)
GO

CREATE TABLE [UserReport]
(
      [UserRportID] int PRIMARY KEY,
      [SendDate] date,
      [FileData] varchar(50),
      [UserID] int,
      [FileID] int
)
GO

ALTER TABLE [UserReport] ADD FOREIGN KEY ([FileID]) REFERENCES [File] ([FileID])
GO

ALTER TABLE [UserReport] ADD FOREIGN KEY ([UserID]) REFERENCES [User] ([UserID])
GO

ALTER TABLE [Scheduler] ADD FOREIGN KEY ([HospitalSystemRegionID]) REFERENCES [HospitalSystemRegion] ([HospitalSystemRegionID])
GO

ALTER TABLE [Scheduler] ADD FOREIGN KEY ([ScheduleFrequencyID]) REFERENCES [ScheduleFrequency] ([ScheduleFrequencyID])
GO

ALTER TABLE [Scheduler] ADD FOREIGN KEY ([SchedulePeriodID]) REFERENCES [SchedulePeriod] ([SchedulePeriodID])
GO

ALTER TABLE [Scheduler] ADD FOREIGN KEY ([ScheduleTaskID]) REFERENCES [ScheduleTask] ([ScheduleTaskID])
GO

ALTER TABLE [Recipients] ADD FOREIGN KEY ([ScheduleID]) REFERENCES [Scheduler] ([ScheduleID])
GO

ALTER TABLE [Recipients] ADD FOREIGN KEY ([UserID]) REFERENCES [User] ([UserID])
GO

ALTER TABLE [User] ADD FOREIGN KEY ([RoleID]) REFERENCES [Role] ([RoleID])
GO

ALTER TABLE [Scheduler] ADD FOREIGN KEY ([FileID]) REFERENCES [File] ([FileID])
GO

ALTER TABLE [User] ADD FOREIGN KEY ([HospitalSystemRegionID]) REFERENCES [HospitalSystemRegion] ([HospitalSystemRegionID])
GO

ALTER TABLE [HospitalSystemRegion] ADD FOREIGN KEY ([HospitalSystemID]) REFERENCES [HospitalSystem] ([HospitalSystemID])
GO

ALTER TABLE [File] ADD FOREIGN KEY ([HospitalSystemRegionID]) REFERENCES [HospitalSystemRegion] ([HospitalSystemRegionID])
GO