#! /usr/bin/env python3.9

# ==========================================================================
#  Copyright (c) Orison AI, 2024.
#
#  All rights reserved. All hardware and software names used are registered
#  trade names and/or registered trademarks of the respective manufacturers.
#
#  The user of this computer program acknowledges that the above copyright
#  notice, which constitutes the Universal Copyright Convention, will be
#  attached at the position in the function of the computer program which the
#  author has deemed to sufficiently express the reservation of copyright.
#  It is prohibited for customers, users and/or third parties to remove,
#  modify or move this copyright notice.
# ==========================================================================

from private_gpt.di import global_injector


def get_motor_db(db_namespace, event_loop=None, asyncio_client=True):
    """
    Gets the motor db client given the specified parameter namespace

    Warning: the returned client will only work with the specified event_loop
    or the current event loop if None! If using multiple event loops, be very
    careful to create separate clients and not to share futures between them

    :param db_namespace: The parameter namespace
    :type db_namespace: str
    :param event_loop: The event loop to use
    :type event_loop: Union[asyncio.AbstractEventLoop, ioloop.IOLoop, None]
    :param asyncio_client: True if using an asyncio event loop, false for tornado
    :rtype: Union[motor.motor_tornado.MotorClient, motor.motor_asyncio.AsyncIOMotorClient]
    """

    db_params = get_param(db_namespace)
    with _lock:
        override_value = _override_hosts.get(db_namespace, None)
        if override_value:
            db_params["host"] = override_value
    return get_motor_db_params(db_params, event_loop, asyncio_client)


def get_motor_db_params(params, event_loop=None, asyncio_client=True):
    """
    Gets the motor db client given the specified parameter namespace

    Warning: the returned client will only work with the specified event_loop
    or the current event loop if None! If using multiple event loops, be very
    careful to create separate clients and not to share futures between them

    :param params: The parameters to use
    :type params: dict
    :param event_loop: The event loop to use
    :type event_loop: Union[asyncio.AbstractEventLoop, ioloop.IOLoop, None]
    :param asyncio_client: True if using an asyncio event loop, false for tornado
    :rtype: Union[motor.motor_tornado.MotorClient, motor.motor_asyncio.AsyncIOMotorClient]
    """

    host = params["host"]
    database_name = params["name"]
    return get_motor_db_host_database(host, database_name, event_loop, asyncio_client)


def get_motor_db_host_database(
    host, database_name, event_loop=None, asyncio_client=True
):
    """
    Gets the motor db client given the specified parameter namespace

    Warning: the returned client will only work with the specified event_loop
    or the current event loop if None! If using multiple event loops, be very
    careful to create separate clients and not to share futures between them

    :param host: The parameters to use
    :type  host: str
    :param database_name: The database name
    :type  database_name: str
    :param event_loop: The event loop to use
    :type event_loop: Union[asyncio.AbstractEventLoop, ioloop.IOLoop, None]
    :param asyncio_client: True if using an asyncio event loop, false for tornado
    :type asyncio_client: bool
    :rtype: Union[motor.motor_tornado.MotorClient, motor.motor_asyncio.AsyncIOMotorClient]
    """

    with _lock:
        if event_loop is None:
            event_loop = (
                asyncio.get_event_loop() if asyncio_client else IOLoop.current()
            )
        database = _databases.get((host, event_loop, database_name))
        if database:
            return database

        client = _motor_clients.get((host, event_loop))
        if not client:
            _logger.debug("Creating Motor Client for: %s", host)

            if six.PY2 and asyncio_client:
                raise Exception("Asyncio clients not supported on Python 2!")

            client_type = AsyncIOMotorClient if asyncio_client else MotorClient
            client = client_type(host, io_loop=event_loop)
            _motor_clients[(host, event_loop)] = client

            # TODO (JF) MERGE WITH MOTOR CLIENT FIXTURE CHANGES
            # def shutdown():
            #     del _motor_clients[(host, event_loop)]
            #     client.shutdown()
            # register_sync_shutdown_callback(shutdown)

        database = client[database_name]
        _databases[(host, event_loop, database_name)] = database
        return database
