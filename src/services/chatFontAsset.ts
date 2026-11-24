import { Asset } from 'expo-asset';
import { Platform } from 'react-native';
import fontManifest from '../../assets/terminal-fonts/manifest.json';
import { IOS_TERMINAL_ASSETS } from './terminalAssets';

// Reuse the terminal's packaged OpenType font instead of bundling another Metro copy.
const uri = Platform.OS === 'ios'
  ? `${IOS_TERMINAL_ASSETS?.directoryURL?.replace(/\/$/, '')}/${fontManifest.cjk.bundledRegularFile}`
  : `asset:///${fontManifest.cjk.bundledRegularFile}`;

export const chatCjkFontAsset = new Asset({ name: 'WhipChatCJK', type: 'otf', uri });
chatCjkFontAsset.localUri = uri;
chatCjkFontAsset.downloaded = true;
