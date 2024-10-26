// API data
const baseUrl2 = 'https://analytics.api.aiesec.org/v2/applications/analyze';
const accessToken2 = '0b085db925bfe08eb8b7acbe9c53eefd26fbe6347cb943ac1da87b1204e5c8db';

// Constants
const entitiesList2 = [
    { id: 222, name: 'CC' },
    { id: 872, name: 'CN' },
    { id: 1340, name: 'CS' },
    { id: 221, name: 'USJ' },
    { id: 2204, name: 'Kandy' },
    { id: 2175, name: 'Ruhuna' },
    { id: 2188, name: 'SLIIT' },
    { id: 2186, name: 'NSBM' },
    { id: 4535, name: 'NIBM' },
    { id: 5490, name: 'Rajarata' }
];


const regexList2 = [
  // {name: "Total", pattern: /^.*_total$/},

  {name: "oGV", pattern: /^o_.*_[7]$/},
  {name: "oGTa", pattern: /^o_.*_[8]$/},
  {name: "oGTe", pattern: /^o_.*_[9]$/},

  {name: "iGV", pattern: /^i_.*_[7]$/},
  {name: "iGTa", pattern: /^i_.*_[8]$/},
  {name: "iGTe", pattern: /^i_.*_[9]$/}
];

// Configs
const startDate2 = '2024-10-26';
const endDate2 = '2024-10-28';

const sheetName2 = "Reset"

const keysList2 = [
  // "matched",
  "applied",
  // "an_accepted",
  "approved",
  // "realized",
  // "remote_realized",
  // "finished",
  // "completed"
]

const headersList2 = [
  "Entity",
  "Function",
  // "Matched",
  "Applied",
  // "An-Accepted",
  "Approved",
  // "Realized",
  // "Remote Realized",
  // "Finished",
  // "Completed",
  // "APP_Points",
  // "APD_Points"
]

// Helper functions
function fetchData2(startDate2, endDate2) {
  const url = `${baseUrl2}?access_token=${accessToken2}&start_date=${startDate2}&end_date=${endDate2}&performance_v3[office_id]=${1623}`;
  const json = UrlFetchApp.fetch(url).getContentText();
  const data = JSON.parse(json);
  return data;
}

function extractData2(apiOutput) {
  let extractedData = {}

  regexList.forEach((regex) => {
    let obj = {}

    const regexMatches = Object.entries(apiOutput).filter(([key, value]) => regex.pattern.test(key));

    regexMatches.forEach((match)=> {
      keysList2.forEach((key) => {
        if(match[0].includes(key)){
          obj[key] = obj[key] ? obj[key] : 0 + (match[1]?.doc_count || 0)
        };
      });

      // Add any more calculations here

      // if(match[0].includes("applied")){
      //     obj["app_points"] = match[1]?.applicants?.value * 10;
      // }

      // if(match[0].includes("approved")){
      //     obj["apd_points"] = match[1]?.applicants?.value * 30;
      // }
    })

    extractedData[regex.name] = obj
  })

  return extractedData;
}

function prepareSheet2() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName2);

  if (!sheet) {
    throw new Error($`Sheet with name ${sheetName2} does not exist.`);
  }

  sheet.getRange(1, 1, 1 , headersList.length).setValues([headersList2]); 
}

function writeRowToSheet2(rowIndex, rowData){
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName2);

    // row --- int --- top row of the range
    // column --- int--- leftmost column of the range
    // optNumRows --- int --- number of rows in the range
    // optNumColumns --- int --- number of columns in the range
    sheet.getRange(1 + rowIndex, 1, 1 , rowData.length).setValues([rowData]); 
}

// =================

function startProcess2(){
  console.log("Starting process...");
  prepareSheet2();

  let finalOutput = {}
  let allData= fetchData2(startDate2, endDate2);

  console.log("Fetching data...")
  entitiesList.forEach((entity) => {
    let entityData=allData[entity.id.toString()]
    console.log(entityData)
    const extractedData = extractData2(entityData);

    finalOutput[entity.name] = extractedData;
  });

  console.log(finalOutput);
  console.log("Writing to sheet edited...");

  entitiesList.forEach((entity, index1) => {
    regexList.forEach((regex, index2)=> {
      const dynamicColumns = keysList.map((key) => finalOutput[entity.name][regex.name][key]);

        const rowData = [
        entity.name,
        regex.name,
        ...dynamicColumns
      ];

    writeRowToSheet2((index1 * regexList.length)+(index2+1), rowData);
    });
  });

  console.log("Done writing to sheet :)");
}