import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.interactions.Actions;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.*;
import java.util.concurrent.TimeUnit;

public class PhotoDownloader {

    private WebDriver driver;

    /**
     * init function that sets the webDriver will use with the options and arguments we want for this project.
     */
    public PhotoDownloader() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--disable-blink-features=AutomationControlled");
        options.addArguments("--lang=he");
        options.setExperimentalOption("useAutomationExtension", false);
        options.setExperimentalOption("excludeSwitches", new String[]{"enable-automation"});

//        String[] useragentarray = {
//                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
//                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
//        };
//
//        for (String userAgent : useragentarray) {
//            options.addArguments("--user-agent=" + userAgent);
//        }

        this.driver = new ChromeDriver(options);

        // Remove navigator.webdriver to avoid detection
        ((JavascriptExecutor) driver).executeScript("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})");
    }

    // Creating dictionaries of the months that maps the words to numbers (in strings)
    private static final Map<String, String> hebrewMonths = Map.ofEntries(
            Map.entry("בינו", "01"),
            Map.entry("בפבר", "02"),
            Map.entry("במרץ", "03"),
            Map.entry("באפר", "04"),
            Map.entry("במאי", "05"),
            Map.entry("ביוני", "06"),
            Map.entry("ביולי", "07"),
            Map.entry("באוג", "08"),
            Map.entry("בספט", "09"),
            Map.entry("באוק", "10"),
            Map.entry("בנוב", "11"),
            Map.entry("בדצמ", "12")
    );

    private static final Map<String, String> englishMonths = Map.ofEntries(
            Map.entry("Jan", "01"),
            Map.entry("Feb", "02"),
            Map.entry("Mar", "03"),
            Map.entry("Apr", "04"),
            Map.entry("May", "05"),
            Map.entry("Jun", "06"),
            Map.entry("Jul", "07"),
            Map.entry("Aug", "08"),
            Map.entry("Sept", "09"),
            Map.entry("Oct", "10"),
            Map.entry("Nov", "11"),
            Map.entry("Dec", "12")
    );

    private static final Map<String, Object[]> readyFiles = new HashMap<>();

//    public static void main(String[] args) {
//        makeDirectory("C:\\Users\\galev\\OneDrive\\Desktop", "Google Photos");
//        String pathStr = "C:\\Users\\galev\\OneDrive\\Desktop\\Google Photos";
//        crawler("https://photos.google.com/photo/AF1QipOHd5Z-gMuMUxXd9zj0QHEl13-L1dCGw4txRUZS", pathStr,
//                true, false, 3, true, "galevi403", "Gal140921Tehila");
//    }

    public static String makeDirectory(String path, String directoryName) {
        String completePath = path + "\\" + directoryName;
        File directory = new File(completePath);
        if (!directory.exists()) {
            directory.mkdir();
        }
        else {
            System.out.println("Directory already exists");
        }
        return completePath;
    }


    public void killDriver(){
        this.driver.quit();
    }

    public static boolean directoryExists(String directoryPath) {
        File directory = new File(directoryPath);
        return directory.exists() && directory.isDirectory();
    }

    public static String getLanguage(WebDriver driver, String url) {
        String language = (String) ((JavascriptExecutor)driver).executeScript("return navigator.language || navigator.userLanguage;");
        System.out.println("Browser Language: " + language);
        if (language.startsWith("en")) {
            return "english";
        }

        WebElement element = driver.findElement(By.tagName("body"));
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        element.sendKeys(Keys.ARROW_LEFT);
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        if (driver.getCurrentUrl().equals(url)) {
            element.sendKeys(Keys.ARROW_RIGHT);
            try {
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            element.sendKeys(Keys.ARROW_LEFT);
            return "english";
        } else {
            element.sendKeys(Keys.ARROW_RIGHT);
            try {
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            return "hebrew";
        }
    }

    public static void moveToNextPhoto(WebDriver driver, String direction) {
        Actions actions = new Actions(driver);
        WebElement element = driver.findElement(By.tagName("body"));
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        actions.click(element).perform();
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        if (direction.equals("right")) {
            element.sendKeys(Keys.ARROW_RIGHT);
        } else {
            element.sendKeys(Keys.ARROW_LEFT);
        }
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void deletePhoto(WebDriver driver) {
        WebElement element = driver.findElement(By.tagName("body"));
        element.click();
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        element.sendKeys(Keys.SHIFT + "#");
        try {
            TimeUnit.SECONDS.sleep(2);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.switchTo().activeElement().sendKeys(Keys.ENTER);
        try {
            TimeUnit.SECONDS.sleep(2);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static double getFileSize(String fileDetails) {
        int sizeStart = fileDetails.indexOf('(') + 1;
        int sizeEnd = fileDetails.indexOf(')', sizeStart);

        String sizeStr = fileDetails.substring(sizeStart, sizeEnd).trim();
        String[] sizeParts = sizeStr.split(" ");
        double sizeValue = Double.parseDouble(sizeParts[0]);
        String sizeUnit = sizeParts[1].toUpperCase();

        if (sizeUnit.equals("MB")) {
            return sizeValue;
        } else if (sizeUnit.equals("GB")) {
            return sizeValue * 1024;
        } else {
            return sizeValue / 1024;
        }
    }

    public static boolean isVideo(WebDriver driver) {
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        WebElement parentElement = driver.findElement(By.xpath("/html/body/div[1]"));
        String parentContent = parentElement.getText();
        double size = 0;
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        if (parentContent.contains(".mp4")) {
            size = getFileSize(parentContent);
            return true;
        }
        return false;
    }

    public static String[] getFileDateAndName(WebDriver driver, String language) {
        WebElement divElement = driver.findElement(By.xpath("//div[@aria-live='assertive']"));
        String date = divElement.getAttribute("innerHTML");
        date = date.replace('\u200F', ' ');
        String[] dateAsArray = date.split(" ");
        for (int i = 0; i < dateAsArray.length; i++) {
            dateAsArray[i] = dateAsArray[i].replace(",", "");
        }
        String day = dateAsArray[4];
        String month = hebrewMonths.getOrDefault(dateAsArray[5].replace("׳", ""), englishMonths.get(dateAsArray[5].replace("׳", "")));
        String year = dateAsArray[6];
        String exactTime = dateAsArray[7];

        String fileDate = year + ":" + month + ":" + day + " " + exactTime;
        String fileName = day + "_" + month + "_" + year + " " + exactTime.replace(':', '_');
        return new String[]{fileDate, fileName};
    }

    public static String checkFileName(String name, String directoryPath, boolean isVideo) {
        String suffix = isVideo ? ".mp4" : ".jpg";
        String filePath = directoryPath + "\\" + name;
        int imageCount = 0;
        while (new File(filePath).exists()) {
            imageCount++;
            filePath = directoryPath + "\\" + name + "(" + imageCount + ")";
        }
        if (imageCount == 0) {
            return name;
        }
        return name + "(" + imageCount + ")";
    }

    public static void saveImageAs(String name, String directoryPath, WebDriver driver, WebElement element) {
        Actions actions = new Actions(driver);
        actions.contextClick(element).perform();
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(2);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void saveVideoAs(String name, String directoryPath, WebDriver driver, double videoSize) {
        Actions actions = new Actions(driver);
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void setMetadata(String filePath, String dateStr) {
        // Implement metadata setting using a Java library
    }

    public static String downloadAndSaveFile(WebDriver driver, String language, String directoryPath, double videoSize, boolean isVideo) {
        String[] fileInfo = getFileDateAndName(driver, language);
        String fileDate = fileInfo[0];
        String fileName = fileInfo[1];
        String year = fileDate.substring(0, 4);
        String month = fileDate.substring(5, 7);
        String directoryName = year + "." + month;
        String currentDirectory = directoryPath + "\\" + directoryName;

        if (!directoryExists(currentDirectory)) {
            new File(currentDirectory).mkdir();
        }

        WebElement element = driver.findElement(By.tagName("body"));
        fileName = checkFileName(fileName, currentDirectory, isVideo);
        if (isVideo) {
            saveVideoAs(fileName, currentDirectory, driver, videoSize);
        } else {
            saveImageAs(fileName, currentDirectory, driver, element);
        }
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        setMetadata(currentDirectory + "\\" + fileName + ".jpg", fileDate);
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return currentDirectory;
    }

    public static void renameAndMove(String downloadsDirectory, String originalName) {
        Object[] fileTuple = readyFiles.get(originalName);
        String fileName = (String) fileTuple[0];
        String directoryPath = (String) fileTuple[1];
        boolean isVideo = (boolean) fileTuple[2];
        String fileDate = (String) fileTuple[3];
        if (!directoryExists(directoryPath)) {
            new File(directoryPath).mkdir();
        }
        fileName = checkFileName(fileName, directoryPath, isVideo);
        String oldNamePath = downloadsDirectory + "\\" + originalName;
        String suffix = isVideo ? ".mp4" : ".jpg";
        String newNamePath = directoryPath + "\\" + fileName + suffix;
        try {
            Files.move(Paths.get(oldNamePath), Paths.get(newNamePath), StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            e.printStackTrace();
        }
        setMetadata(newNamePath, fileDate);
    }

    public static String downloadAndCollectData(WebDriver driver, String language, String directoryPath) {
        WebElement element = driver.findElement(By.tagName("body"));
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        String[] fileInfo = getFileDateAndName(driver, language);
        String fileDate = fileInfo[0];
        String fileName = fileInfo[1];
        String year = fileDate.substring(0, 4);
        String month = fileDate.substring(5, 7);
        String directoryName = year + "." + month;
        String designatedDirectoryPath = directoryPath + "\\" + directoryName;
        element.sendKeys("i");
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        WebElement parentElement = driver.findElement(By.xpath("/html/body/div[1]"));
        String parentContent = parentElement.getText();
        element.sendKeys(Keys.SHIFT + "d");
        element.sendKeys("i");
        boolean isVideo = parentContent.contains(".mp4");
        String[] parentText = parentContent.split("\n");
        String originalName = "";
        for (String line : parentText) {
            if (isVideo && line.endsWith("mp4")) {
                originalName = line;
                break;
            } else if (!isVideo && line.endsWith("jpg")) {
                originalName = line;
                break;
            }
        }
        readyFiles.put(originalName, new Object[]{fileName, designatedDirectoryPath, isVideo, fileDate});
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return originalName;
    }

    public static String[] setDirection(String language, boolean olderPhotos) {
        if (language.equals("hebrew")) {
            if (olderPhotos) {
                return new String[]{"left", "right"};
            } else {
                return new String[]{"right", "left"};
            }
        } else {
            if (olderPhotos) {
                return new String[]{"right", "left"};
            } else {
                return new String[]{"left", "right"};
            }
        }
    }

    public static String getDownloadDirectory(WebDriver driver, String language) {
        driver.get("chrome://settings/downloads");
        WebElement element = driver.findElement(By.tagName("settings-ui"));
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        WebElement shadowRoot = getShadowRoot(driver, element);
        String shadowRootText = shadowRoot.findElement(By.cssSelector("#main")).getText();
        String[] textAsArray = shadowRootText.split("\n");
        List<String> textAsList = Arrays.asList(textAsArray);

        int pathIndex = language.equals("english") ? textAsList.indexOf("Location") + 1 : textAsList.indexOf("מיקום") + 1;
        return textAsArray[pathIndex];
    }

    public static WebElement getShadowRoot(WebDriver driver, WebElement element) {
        return (WebElement) ((JavascriptExecutor)driver).executeScript("return arguments[0].shadowRoot", element);
    }

    public void crawler(String url, String directoryPath, boolean olderPhotos, boolean downloadAllPhotos, int numberOfPhotos, boolean delete, String username, String password) {


        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.get(url);

        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // Simulate keyboard input
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        String downloadDirectory = getDownloadDirectory(driver, "hebrew");
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.get(url);
        while (!driver.getCurrentUrl().equals(url)) {
            try {
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        String[] direction = setDirection("hebrew", olderPhotos);
        moveToNextPhoto(driver, direction[0]);
        moveToNextPhoto(driver, direction[1]);

        if (downloadAllPhotos) {
            String previousUrl = url;
            String currentUrl = null;
            while (!previousUrl.equals(currentUrl)) {
                previousUrl = currentUrl;
                boolean isFileVideo = isVideo(driver);
                downloadAndCollectData(driver, "hebrew", directoryPath);
                try {
                    TimeUnit.SECONDS.sleep(1);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                if (delete) {
                    deletePhoto(driver);
                    try {
                        TimeUnit.SECONDS.sleep(2);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (!olderPhotos) {
                        previousUrl = driver.getCurrentUrl();
                        try {
                            TimeUnit.SECONDS.sleep(2);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                        moveToNextPhoto(driver, direction[0]);
                        try {
                            TimeUnit.SECONDS.sleep(2);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    }
                }
                currentUrl = driver.getCurrentUrl();
            }
        } else {
            String previousUrl = url;
            String currentUrl = null;
            for (int i = 0; i < numberOfPhotos; i++) {
                if (previousUrl.equals(currentUrl)) {
                    break;
                }
                previousUrl = currentUrl;
                String originalName = downloadAndCollectData(driver, "hebrew", directoryPath);
                if (delete) {
                    deletePhoto(driver);
                    if (!olderPhotos) {
                        previousUrl = driver.getCurrentUrl();
                        moveToNextPhoto(driver, direction[0]);
                        try {
                            TimeUnit.SECONDS.sleep(1);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    }
                }
                renameAndMove(downloadDirectory, originalName);
                currentUrl = driver.getCurrentUrl();
            }
        }
        driver.quit();
    }
}

