# Now we create the functions that agents can call to retrieve information.
# We will create four music tools and three invoice tools, following the reference notebook.

import json

from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from database.chinook import execute_query


# ==========================================
# MUSIC AGENT TOOLS
# ==========================================

@tool
def get_albums_by_artist(artist: str):
    """Find albums belonging to a particular artist."""

    query = """
        SELECT Album.Title, Artist.Name AS Artist
        FROM Album
        JOIN Artist
        ON Album.ArtistId = Artist.ArtistId
        WHERE Artist.Name LIKE ?
    """

    return execute_query(query, (f"%{artist}%",))


@tool
def get_tracks_by_artist(artist: str):
    """Find tracks belonging to an artist."""

    query = """
        SELECT Track.Name AS Song,
               Artist.Name AS Artist,
               Album.Title AS Album
        FROM Track
        JOIN Album ON Track.AlbumId = Album.AlbumId
        JOIN Artist ON Album.ArtistId = Artist.ArtistId
        WHERE Artist.Name LIKE ?
        LIMIT 30
    """

    return execute_query(query, (f"%{artist}%",))


@tool
def get_songs_by_genre(genre: str):
    """Find songs belonging to a music genre."""

    query = """
        SELECT Track.Name AS Song,
               Artist.Name AS Artist,
               Genre.Name AS Genre
        FROM Track
        JOIN Genre ON Track.GenreId = Genre.GenreId
        JOIN Album ON Track.AlbumId = Album.AlbumId
        JOIN Artist ON Album.ArtistId = Artist.ArtistId
        WHERE Genre.Name LIKE ?
        LIMIT 30
    """

    return execute_query(query, (f"%{genre}%",))


@tool
def check_for_songs(song_title: str):
    """Check whether a particular song exists."""

    query = """
        SELECT Name
        FROM Track
        WHERE Name LIKE ?
        LIMIT 20
    """

    return execute_query(query, (f"%{song_title}%",))


music_tools = [
    get_albums_by_artist,
    get_tracks_by_artist,
    get_songs_by_genre,
    check_for_songs
]


# ==========================================
# INVOICE AGENT TOOLS
# ==========================================

@tool
def get_invoices_by_customer_sorted_by_date(
    runtime: ToolRuntime
):
    """Get invoices for the currently verified customer,
    sorted by newest invoice first."""

    customer_id = runtime.state.get("customer_id")

    if customer_id is None:
        return "Customer is not verified."

    query = """
        SELECT *
        FROM Invoice
        WHERE CustomerId = ?
        ORDER BY InvoiceDate DESC
    """

    return execute_query(query, (customer_id,))


@tool
def get_invoices_sorted_by_unit_price(
    runtime: ToolRuntime
):
    """Find invoice line items sorted by unit price."""

    customer_id = runtime.state.get("customer_id")

    if customer_id is None:
        return "Customer is not verified."

    query = """
        SELECT Invoice.InvoiceId,
               Invoice.InvoiceDate,
               InvoiceLine.UnitPrice,
               InvoiceLine.Quantity,
               Track.Name AS Song
        FROM Invoice
        JOIN InvoiceLine
        ON Invoice.InvoiceId = InvoiceLine.InvoiceId
        JOIN Track
        ON InvoiceLine.TrackId = Track.TrackId
        WHERE Invoice.CustomerId = ?
        ORDER BY InvoiceLine.UnitPrice DESC
    """

    return execute_query(query, (customer_id,))


@tool
def get_employee_by_invoice_and_customer(
    runtime: ToolRuntime,
    invoice_id: int
):
    """Find the support employee associated with an invoice."""

    customer_id = runtime.state.get("customer_id")

    if customer_id is None:
        return "Customer is not verified."

    query = """
        SELECT Employee.FirstName,
               Employee.LastName,
               Employee.Title,
               Employee.Email
        FROM Employee
        JOIN Customer
        ON Customer.SupportRepId = Employee.EmployeeId
        JOIN Invoice
        ON Invoice.CustomerId = Customer.CustomerId
        WHERE Invoice.InvoiceId = ?
        AND Invoice.CustomerId = ?
    """

    return execute_query(
        query,
        (invoice_id, customer_id)
    )


invoice_tools = [
    get_invoices_by_customer_sorted_by_date,
    get_invoices_sorted_by_unit_price,
    get_employee_by_invoice_and_customer
]
