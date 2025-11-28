CREATE DATABASE [ElectroPunoETL];
GO

USE [ElectroPunoETL];
GO

CREATE TABLE [dbo].[Client] (
    [client_id] INT PRIMARY KEY
);
GO

CREATE TABLE [dbo].[Period] (
    [period_id] INT IDENTITY(1,1) PRIMARY KEY,
    [year] SMALLINT NOT NULL,
    [month] TINYINT NOT NULL,
);
GO

CREATE TABLE [dbo].[Location] (
    [location_id] INT IDENTITY(1,1) PRIMARY KEY,
    [ubigeo] CHAR(6) NOT NULL,
    [district] VARCHAR(200) NOT NULL,
    [province] VARCHAR(200) NOT NULL,
    [department] VARCHAR(200) NOT NULL
);
GO

CREATE TABLE [dbo].[Fact] (
    [client_id] INT NOT NULL,
    [period_id] INT NOT NULL,
    [location_id] INT NOT NULL,
    [amount] DECIMAL(9,2) NULL,
    [consumption] DECIMAL(9,2) NULL,
    [client_state] CHAR(2) NULL,
    CONSTRAINT [FK_Fact_Client] FOREIGN KEY ([client_id]) REFERENCES [dbo].[Client] ([client_id]),
    CONSTRAINT [FK_Fact_Period] FOREIGN KEY ([period_id]) REFERENCES [dbo].[Period] ([period_id]),
    CONSTRAINT [FK_Fact_Location] FOREIGN KEY ([location_id]) REFERENCES [dbo].[Location] ([location_id])
);
GO