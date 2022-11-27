from ctypes import Union
from datetime import datetime, time
from http.client import HTTPException
from typing import Optional, Union
from fastapi import FastAPI, status, Security, Query, HTTPException
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import uvicorn
from enum import Enum


app = FastAPI()

class Fila(BaseModel):
  id: Optional[int] = 0
  nome: str = Query(max_length=20)
  data_chegada: datetime
  prioridade: Union[str, None] = Query(default="N", max_length=1)
  atendido: Optional[bool] = False


API_KEY = "123asd"
APY_KEY_NAME = "Authorization"
api_key_header_auth = APIKeyHeader(name=APY_KEY_NAME, auto_error=True)

def get_api_key(api_key_header = Security(api_key_header_auth)):
  if api_key_header != API_KEY:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail = "Invalid API Key")


@app.get("/protected", dependencies=[Security(get_api_key)])
def root():
  return {"message" : "Conteúdo Seguro"}

@app.post("/fila/", status_code=status.HTTP_201_CREATED)
def add_fila(fila: Fila): 
  if fila.prioridade == "N" or fila.prioridade == "P":
    if db_fila:
      fila.id = db_fila[-1].id + 1
    else:
      fila.id = 1
    db_fila.append(fila)
    return {"fila": "Aguarde ser chamado!"}
  else:
    return {"Digite N para atendimento normal ou P para atendimeto prioritário."}

@app.get("/fila")
def exibir_fila():
  return {"fila": db_fila}

@app.get("/fila/{id}")
def posicao_fila(id: int):
  for fila in db_fila:
    if fila.id == id:
      status_code=status.HTTP_200_OK
      return {"id": fila.id, "nome": fila.nome, "data": fila.data_chegada}
  return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posição não encontrada!")
  


@app.put("/fila/atender")
def atender_cliente():
  if len(db_fila) == 0:
    return {"Fila Vazia!"}
  db_fila[0].atendido = True
  aux = db_fila[0]
  db_fila.remove(aux)
  return {"Próximo: ": aux}


@app.delete("/fila/{id}", status_code=status.HTTP_200_OK)
def delete_fila(id: int):
  fila = [fila for fila in db_fila if fila.id == id]
  db_fila.remove(fila[0])
  return {"mensagem": "ID removido!"}

db_fila =[]

if __name__ == "__main__":
  uvicorn.run(app,host= "127.0.0.1", port = 8000)