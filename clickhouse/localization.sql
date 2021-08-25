CREATE TABLE real_data_prod.localization
(
    `id` String,
    `timestamp` DateTime('Europe/Warsaw'),
    `lon` Float32,
    `lat` Float32
)
ENGINE = TinyLog
