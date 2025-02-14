// Exemple : dans ExtractionListComponent ngOnInit() ou dans le constructeur :
this.columnDefs.push({
  headerName: 'Edit',
  field: 'edit',
  cellRenderer: (params) => {
    const eGui = document.createElement('div');
    eGui.innerHTML = `<cib-icon name="ic_edit" context="Update" class="ald-ico-upt"></cib-icon>`;
    eGui.querySelector('.ald-ico-upt')?.addEventListener('click', () => {
      this.onCLickBtnUpdateAction(params.data);
    });
    return eGui;
  }
});

this.columnDefs.push({
  headerName: 'Run',
  field: 'run',
  cellRenderer: (params) => {
    const eGui = document.createElement('div');
    eGui.innerHTML = `<cib-icon name="ic_arrow_right" context="Run" class="ald-ico-run"></cib-icon>`;
    eGui.querySelector('.ald-ico-run')?.addEventListener('click', () => {
      this.onCLickBtnLaunchAction(params.data);
    });
    return eGui;
  }
});

this.columnDefs.push({
  headerName: 'Delete',
  field: 'delete',
  cellRenderer: (params) => {
    const eGui = document.createElement('div');
    eGui.innerHTML = `<cib-icon name="ic_delete" context="Delete" class="ald-ico-del"></cib-icon>`;
    eGui.querySelector('.ald-ico-del')?.addEventListener('click', () => {
      this.onClickBtnRemoveAction(params.data);
    });
    return eGui;
  }
});

this.columnDefs.push({
  headerName: 'Export',
  field: 'export',
  cellRenderer: (params) => {
    const eGui = document.createElement('div');
    eGui.innerHTML = `<cib-icon name="ic_download" context="Export" class="ald-ico-export"></cib-icon>`;
    eGui.querySelector('.ald-ico-export')?.addEventListener('click', () => {
      this.onClickBtnExportAction(params.data);
    });
    return eGui;
  }
});
