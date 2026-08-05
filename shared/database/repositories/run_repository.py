from datetime import datetime

from shared.constants import (
    RUN_RUNNING,
    RUN_SUCCESS,
    RUN_FAILED
)

from shared.utils.run_id import generate_run_id


def create_run(connection):

    run_id = generate_run_id()

    cursor = connection.cursor()

    query = """
        INSERT INTO inventory_run
        (
            run_id,
            source_system,
            started_at,
            status_id
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """

    cursor.execute(
        query,
        (
            run_id,
            "QueueBuster",
            datetime.now(),
            RUN_RUNNING
        )
    )

    cursor.close()

    return run_id


def complete_run(
    connection,
    run_id,
    stores_processed,
    stores_failed,
    products_processed,
    rows_inserted,
    duration_seconds
):

    cursor = connection.cursor()

    query = """
        UPDATE inventory_run
        SET
            completed_at=%s,
            status_id=%s,
            stores_processed=%s,
            stores_failed=%s,
            products_processed=%s,
            rows_inserted=%s,
            duration_seconds=%s
        WHERE run_id=%s
    """

    cursor.execute(
        query,
        (
            datetime.now(),
            RUN_SUCCESS,
            stores_processed,
            stores_failed,
            products_processed,
            rows_inserted,
            duration_seconds,
            run_id
        )
    )

    cursor.close()


def fail_run(connection, run_id):

    cursor = connection.cursor()

    query = """
        UPDATE inventory_run
        SET
            completed_at=%s,
            status_id=%s
        WHERE run_id=%s
    """

    cursor.execute(
        query,
        (
            datetime.now(),
            RUN_FAILED,
            run_id
        )
    )

    cursor.close()