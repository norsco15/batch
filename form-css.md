.example-list {
  width: 1000px;
  border: solid 1px #ccc;
  min-height: 60px;
  display: flex;
  background: white;
  border-radius: 4px;
  overflow: scroll;
}

.example-box {
  padding: 5px 2px;
  border-right: solid 1px #ccc;
  color: rgba(0, 0, 0, 0.87);
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: normal;
  box-sizing: border-box;
  cursor: move;
  background: white;
  font-size: 12px;
  flex-grow: 1;
  flex-basis: 0;
  /* box-shadow etc. */
}
