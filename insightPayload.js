'use strict';

class InsightsPayload {
  constructor() {
    this.key = '';
    this.returnKey = '';
    this.payload = '';
    this.stampCreated = '';
    this.timeoutSec = 60;
  }
}

module.exports = InsightsPayload;
module.exports.returnKeyPrefix = 'insightClient.return.';
