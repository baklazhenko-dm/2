from typing import List, Optional

from app.schemas.NewNote import NewNote
from app.lib.db import Database
from app.schemas.Note import Note
from app.settings import TITLE_FROM_CONTENT_LEN
from fastapi.exceptions import HTTPException


class NotesController:

    def _row_to_note(self, row: List):
        return Note(
            id=row[0],
            title=row[1] if row[1] is not None else row[2][0:TITLE_FROM_CONTENT_LEN],
            content=row[2]
        )

    async def create_note(self, new_note: NewNote) -> Note:
        await Database.execute('INSERT INTO NOTE(TITLE, CONTENT) VALUES(?, ?);', (new_note.title, new_note.content))
        rows = await Database.fetch_many('SELECT ID, TITLE, CONTENT FROM NOTE ORDER BY ID LIMIT 1')
        row = rows[0]
        note = self._row_to_note(row)
        return note

    async def get_note_by_id(self, note_id: int) -> Note:
        rows = await Database.fetch_many('SELECT ID, TITLE, CONTENT FROM NOTE WHERE ID=?', (note_id,))
        if len(rows) == 0:
            raise HTTPException(status_code=404, detail='Заметка с таким идентификатором не найдена')
        row = rows[0]
        note = self._row_to_note(row)
        return note

    async def update_note_by_id(self, note_id: int, new_note: NewNote) -> Note:
        await Database.execute(
            'UPDATE NOTE SET TITLE=?, CONTENT=? WHERE ID=?',
            (new_note.title, new_note.content, note_id)
        )
        rows = await Database.fetch_many('SELECT ID, TITLE, CONTENT FROM NOTE WHERE ID=?', (note_id,))
        if len(rows) == 0:
            raise HTTPException(status_code=404, detail='Заметка с таким идентификатором не найдена')
        row = rows[0]
        note = self._row_to_note(row)
        return note

    async def get_notes(self, query: Optional[str] = None) -> List[Note]:
        if query is None:
            rows = await Database.fetch_many('SELECT ID, TITLE, CONTENT FROM NOTE')
        else:
            rows = await Database.fetch_many(
                'SELECT ID, TITLE, CONTENT FROM NOTE WHERE INSTR(TITLE, ?) > 0 OR INSTR(CONTENT, ?) > 0',
                (query, query)
            )
        notes: List[Note] = []
        for row in rows:
            notes.append(self._row_to_note(row))
        return notes

    async def delete_note_by_id(self, note_id: int) -> None:
        rows = await Database.fetch_many('SELECT ID, TITLE, CONTENT FROM NOTE WHERE ID=?', (note_id,))
        if len(rows) == 0:
            raise HTTPException(status_code=404, detail='Заметка с таким идентификатором не найдена')
        await Database.execute('DELETE FROM NOTE WHERE ID=?', (note_id,))
