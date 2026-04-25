var ZoteroAddLocalFilePlugin;

function install() {}

async function startup(data, reason) {
  Services.scriptloader.loadSubScript(data.rootURI + "dist/main.js");
  await ZoteroAddLocalFilePlugin.startup(data, reason);
}

async function shutdown(data, reason) {
  if (reason === APP_SHUTDOWN) {
    return;
  }
  if (ZoteroAddLocalFilePlugin) {
    await ZoteroAddLocalFilePlugin.shutdown(data, reason);
  }
  ZoteroAddLocalFilePlugin = undefined;
}

function uninstall() {}

